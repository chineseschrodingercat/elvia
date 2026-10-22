"""Read-only Atlas mount with a fixed, validated file manifest.

Only static bytes are read. Evidence exports are downloads, never programs.
An absent or invalid release disables this mount without disabling the workspace.
"""

from dataclasses import dataclass
import hashlib
import hmac
import json
from pathlib import Path
import re
import stat
from types import MappingProxyType
from urllib.parse import quote, unquote


MANIFEST = "integration-files.json"
ASSET_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}
DOWNLOAD_TYPES = {
    ".json": "application/json; charset=utf-8",
    ".zip": "application/zip",
    ".md": "text/markdown; charset=utf-8",
    ".tex": "application/x-tex",
    ".txt": "text/plain; charset=utf-8",
    ".pdf": "application/pdf",
}


@dataclass(frozen=True)
class FileIdentity:
    sha256: str
    size: int


def _parts(name):
    """Require one canonical portable relative name, including on Windows."""
    if not isinstance(name, str) or not name or len(name) > 1024:
        raise ValueError("invalid Atlas path")
    if any(ord(character) < 32 for character in name) or any(
        character in name for character in "\\:%?#"
    ):
        raise ValueError("invalid Atlas path")
    parts = name.split("/")
    if any(not part or part.startswith(".") or part.endswith((".", " ")) for part in parts):
        raise ValueError("invalid Atlas path")
    if any(re.fullmatch(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part, re.I) for part in parts):
        raise ValueError("invalid Atlas path")
    return parts


class AtlasStatic:
    def __init__(self, root):
        # Retain the lexical root until every component has been checked for links.
        self.root = Path(root).absolute()
        self.files = MappingProxyType({})
        try:
            manifest_path = self._safe_file(MANIFEST)
            if manifest_path.stat().st_size > 8 * 1024 * 1024:
                raise ValueError("Atlas manifest is too large")
            manifest = json.loads(manifest_path.read_bytes())
            if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
                raise ValueError("unsupported Atlas manifest")
            rows = manifest.get("files")
            if not isinstance(rows, list) or not rows:
                raise ValueError("empty Atlas manifest")
            identities = {}
            folded = set()
            for row in rows:
                if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
                    raise ValueError("invalid Atlas manifest entry")
                name, expected = row["path"], row["sha256"]
                _parts(name)
                if name == MANIFEST or name.casefold() in folded:
                    raise ValueError("duplicate or reserved Atlas path")
                if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                    raise ValueError("invalid Atlas hash")
                path = self._safe_file(name)
                size = path.stat().st_size
                with path.open("rb") as stream:
                    actual = hashlib.file_digest(stream, "sha256").hexdigest()
                if not hmac.compare_digest(actual, expected):
                    raise ValueError("Atlas hash mismatch")
                identities[name] = FileIdentity(expected, size)
                folded.add(name.casefold())
            if "index.html" not in identities:
                raise ValueError("Atlas index is missing")
            # Requests never reload this manifest or discover newly added files.
            self.files = MappingProxyType(identities)
        except (OSError, ValueError, TypeError, KeyError):
            # The original contribution preview remains usable without an Atlas.
            self.files = MappingProxyType({})

    def _safe_file(self, name):
        parts = _parts(name)
        candidate = self.root
        for component in (None, *parts):
            if component is not None:
                candidate = candidate / component
            metadata = candidate.lstat()
            if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, "st_file_attributes", 0) & getattr(
                stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400
            ):
                raise ValueError("Atlas links are not allowed")
        resolved_root = self.root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(resolved_root) or not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Atlas path is not a regular in-root file")
        return resolved

    def read(self, encoded_relative):
        """Return exact verified bytes and headers, or None for unavailable paths."""
        try:
            relative = unquote(encoded_relative, errors="strict") or "index.html"
            _parts(relative)
            identity = self.files.get(relative)
            if identity is None:
                return None
            path = self._safe_file(relative)
            if path.stat().st_size != identity.size:
                return None
            # A replacement cannot make an unbounded read, and its bytes still
            # must match the immutable startup identity before any are sent.
            with path.open("rb") as stream:
                body = stream.read(identity.size + 1)
            self._safe_file(relative)
            if len(body) != identity.size or not hmac.compare_digest(
                hashlib.sha256(body).hexdigest(), identity.sha256
            ):
                return None
            suffix = path.suffix.lower()
            download = relative.startswith("evidence/") or suffix not in ASSET_TYPES
            content_type = (DOWNLOAD_TYPES if download else ASSET_TYPES).get(
                suffix, "application/octet-stream"
            )
            headers = {}
            if download:
                headers["Content-Disposition"] = "attachment; filename*=UTF-8''" + quote(path.name, safe="")
            return body, content_type, headers
        except (OSError, ValueError, UnicodeError):
            return None
