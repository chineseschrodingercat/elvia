"""Retain existing credentials and rollback callback while adding the project domain."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "preview/server"), str(ROOT / "scripts")]
from configure_private_auth import checked_data_dir, plain_path, publish, read_json
from google_login import GoogleLogin

PROJECT_ORIGIN = "https://elvia-atlas.org"
LOCAL_CALLBACK = "http://127.0.0.1:8797/api/auth/google/callback"
PREVIOUS_CALLBACK = "https://elvia-private.minhaoliu.com/api/auth/google/callback"
PROJECT_CALLBACK = PROJECT_ORIGIN + "/api/auth/google/callback"
APPROVED_CALLBACKS = (LOCAL_CALLBACK, PREVIOUS_CALLBACK, PROJECT_CALLBACK)


def validate_saved_config(raw):
    """Validate only existing metadata, without silently adding a callback."""
    try:
        if not isinstance(raw, dict):
            raise ValueError()
        web = raw.get("web", raw)
        if not isinstance(web, dict):
            raise ValueError()
        redirects = web.get("redirect_uris", [web.get("redirect_uri")])
        if (not isinstance(redirects, list) or not redirects
                or any(not isinstance(uri, str) or uri not in APPROVED_CALLBACKS
                       for uri in redirects)
                or len(set(redirects)) != len(redirects)
                or LOCAL_CALLBACK not in redirects
                or web.get("redirect_uri", LOCAL_CALLBACK) != LOCAL_CALLBACK):
            raise ValueError()
        normalized = GoogleLogin.validate_config(raw, 8797)
        return {"client_id": normalized["client_id"],
                "client_secret": normalized["client_secret"],
                "redirect_uri": LOCAL_CALLBACK,
                "redirect_uris": [uri for uri in APPROVED_CALLBACKS if uri in redirects]}
    except Exception:
        raise ValueError("Expected the existing valid client and only the three approved callbacks.") from None


def build_project_config(raw):
    result = validate_saved_config(raw)
    result["redirect_uris"] = list(APPROVED_CALLBACKS)
    GoogleLogin.validate_config(result, 8797, private_origin=PROJECT_ORIGIN)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--enable", action="store_true",
                        help="Save the approved project callback, retaining local and previous callbacks")
    args = parser.parse_args()
    try:
        data = checked_data_dir(args.data_dir)
        destination = plain_path(data / "google-oauth.json")
        desired = build_project_config(read_json(destination))
        changed = (publish(data, "google-oauth.json", desired, validate_saved_config, True)
                   if args.enable else False)
        google = GoogleLogin(data, 8797, private_origin=PROJECT_ORIGIN)
        print(json.dumps({"changed": changed,
                          "local_ready": google.public()["enabled"],
                          "project_callback_ready": google.public(PROJECT_ORIGIN)["enabled"],
                          "provider_contacted": False}))
        return 0
    except Exception:
        print("Project callback metadata could not be checked or saved; no credential values are shown.",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
