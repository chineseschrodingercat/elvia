"""Windows boot supervisor: single instance, bounded logs, owned child processes."""

from __future__ import annotations

import argparse
import ctypes
import json
import logging
import subprocess
import sys
import time
from ctypes import wintypes as w
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def plain(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.is_symlink() or (hasattr(item, "is_junction") and item.is_junction()):
            raise ValueError("Linked operational paths are not supported")
    if path.is_file() and path.stat().st_nlink != 1:
        raise ValueError("Hard-linked operational files are not supported")
    return path.resolve()


def load_config(path):
    path = plain(path)
    if path.is_relative_to(ROOT):
        raise ValueError("Operational secrets must stay outside the repository")
    config = json.loads(path.read_text("utf-8-sig"))
    keys = {
        "data_dir",
        "turnstile_sitekey",
        "turnstile_secret",
        "cloudflared",
        "tunnel_token_file",
    }
    if not isinstance(config, dict) or set(config) != keys:
        raise ValueError("Incomplete or unexpected production configuration")
    if any(
        not isinstance(config[k], str) or len(config[k]) < 20
        for k in ("turnstile_sitekey", "turnstile_secret")
    ):
        raise ValueError("Configure the production Turnstile widget first")
    for key in ("data_dir", "cloudflared", "tunnel_token_file"):
        value = plain(config[key])
        if not value.exists() or value.is_relative_to(ROOT):
            raise ValueError("Operational paths must exist outside the repository")
        config[key] = str(value)
    for name in (
        "elvia.sqlite3",
        "email-settings.json",
        "email-verification.key",
        "google-oauth.json",
    ):
        if not plain(Path(config["data_dir"]) / name).is_file():
            raise ValueError(
                "An existing complete operational data directory is required"
            )
    if Path(config["cloudflared"]).name.lower() != "cloudflared.exe":
        raise ValueError("Use the verified Cloudflare connector executable")
    return config


class WindowsProcess:
    """Launch suspended, put in a kill-on-close Job, then resume.

    Holding native handles avoids PID reuse. If the supervisor is killed, Windows
    closes its Job handles and kills both children and Python launcher descendants.
    """

    def __init__(self, arguments):
        self.k = ctypes.WinDLL("kernel32", use_last_error=True)
        k = self.k

        class Basic(ctypes.Structure):
            _fields_ = [
                ("per_process", ctypes.c_longlong),
                ("per_job", ctypes.c_longlong),
                ("flags", w.DWORD),
                ("min_ws", ctypes.c_size_t),
                ("max_ws", ctypes.c_size_t),
                ("active", w.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority", w.DWORD),
                ("scheduling", w.DWORD),
            ]

        class IO(ctypes.Structure):
            _fields_ = [
                (n, ctypes.c_ulonglong)
                for n in (
                    "read_ops",
                    "write_ops",
                    "other_ops",
                    "read_bytes",
                    "write_bytes",
                    "other_bytes",
                )
            ]

        class Extended(ctypes.Structure):
            _fields_ = [
                ("basic", Basic),
                ("io", IO),
                ("process_mem", ctypes.c_size_t),
                ("job_mem", ctypes.c_size_t),
                ("peak_process", ctypes.c_size_t),
                ("peak_job", ctypes.c_size_t),
            ]

        class Startup(ctypes.Structure):
            _fields_ = [
                ("cb", w.DWORD),
                ("reserved", w.LPWSTR),
                ("desktop", w.LPWSTR),
                ("title", w.LPWSTR),
                ("x", w.DWORD),
                ("y", w.DWORD),
                ("xsize", w.DWORD),
                ("ysize", w.DWORD),
                ("xchars", w.DWORD),
                ("ychars", w.DWORD),
                ("fill", w.DWORD),
                ("flags", w.DWORD),
                ("show", w.WORD),
                ("reserved2", w.WORD),
                ("bytes", ctypes.c_void_p),
                ("stdin", w.HANDLE),
                ("stdout", w.HANDLE),
                ("stderr", w.HANDLE),
            ]

        class ProcessInfo(ctypes.Structure):
            _fields_ = [
                ("process", w.HANDLE),
                ("thread", w.HANDLE),
                ("pid", w.DWORD),
                ("tid", w.DWORD),
            ]

        k.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        k.CreateJobObjectW.restype = w.HANDLE
        k.SetInformationJobObject.argtypes = [
            w.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            w.DWORD,
        ]
        k.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        k.CloseHandle.argtypes = [w.HANDLE]
        k.ResumeThread.argtypes = [w.HANDLE]
        k.ResumeThread.restype = w.DWORD
        k.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
        k.GetExitCodeProcess.argtypes = [w.HANDLE, ctypes.POINTER(w.DWORD)]
        k.CreateProcessW.argtypes = [
            w.LPCWSTR,
            w.LPWSTR,
            ctypes.c_void_p,
            ctypes.c_void_p,
            w.BOOL,
            w.DWORD,
            ctypes.c_void_p,
            w.LPCWSTR,
            ctypes.POINTER(Startup),
            ctypes.POINTER(ProcessInfo),
        ]
        self.job, self.process, self.pid = None, None, None
        info = ProcessInfo()
        try:
            self.job = k.CreateJobObjectW(None, None)
            limits = Extended()
            limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not self.job or not k.SetInformationJobObject(
                self.job, 9, ctypes.byref(limits), ctypes.sizeof(limits)
            ):
                raise ctypes.WinError(ctypes.get_last_error())
            startup = Startup()
            startup.cb = ctypes.sizeof(startup)
            command = ctypes.create_unicode_buffer(subprocess.list2cmdline(arguments))
            if not k.CreateProcessW(
                arguments[0],
                command,
                None,
                None,
                False,
                0x08000004,
                None,
                str(ROOT),
                ctypes.byref(startup),
                ctypes.byref(info),
            ):
                raise ctypes.WinError(ctypes.get_last_error())
            self.process, self.pid = info.process, info.pid
            if not k.AssignProcessToJobObject(self.job, self.process):
                k.TerminateProcess(self.process, 1)
                raise ctypes.WinError(ctypes.get_last_error())
            if k.ResumeThread(info.thread) == 0xFFFFFFFF:
                raise ctypes.WinError(ctypes.get_last_error())
        except BaseException:
            self.close()
            raise
        finally:
            if info.thread:
                k.CloseHandle(info.thread)

    def poll(self):
        code = w.DWORD()
        if not self.k.GetExitCodeProcess(self.process, ctypes.byref(code)):
            raise ctypes.WinError(ctypes.get_last_error())
        return None if code.value == 259 else code.value

    def close(self):
        if self.job:
            self.k.CloseHandle(self.job)
            self.job = None
        if self.process:
            self.k.CloseHandle(self.process)
            self.process = None


def supervise(path):
    logs = plain(path).parent / "logs"
    logs.mkdir(exist_ok=True)
    logger = logging.getLogger("elvia-supervisor")
    handler = RotatingFileHandler(
        logs / "service.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        config = load_config(path)
    except Exception as exc:
        logger.error("Configuration validation failed (%s).", type(exc).__name__)
        raise
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, w.BOOL, w.LPCWSTR]
    kernel.CreateMutexW.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    mutex = kernel.CreateMutexW(None, True, "Global\\ELVIA-Website")
    if not mutex or ctypes.get_last_error() == 183:
        logger.error(
            "Could not claim service ownership (Windows error %s).",
            ctypes.get_last_error(),
        )
        raise RuntimeError("Another ELVIA supervisor owns this service")
    commands = {
        "application": [sys.executable, "-m", "website.runtime", "--config", str(path)],
        "connector": [
            config["cloudflared"],
            "tunnel",
            "--no-autoupdate",
            "--loglevel",
            "error",
            "--metrics",
            "127.0.0.1:8800",
            "run",
            "--token-file",
            config["tunnel_token_file"],
        ],
    }
    children, retries, next_attempt = {}, {}, {}
    logger.info(
        "Supervisor started; configuration and request contents omitted from logs."
    )
    try:
        while True:
            now = time.monotonic()
            for name, args in commands.items():
                child = children.get(name)
                if child and child.poll() is not None:
                    logger.warning("%s exited; automatic recovery scheduled.", name)
                    child.close()
                    children.pop(name)
                    next_attempt[name] = now + min(60, 5 * retries.get(name, 1))
                if name not in children and now >= next_attempt.get(name, 0):
                    try:
                        children[name] = WindowsProcess(args)
                        retries[name] = retries.get(name, 0) + 1
                        logger.info("%s started (pid %s).", name, children[name].pid)
                    except OSError as exc:
                        logger.error(
                            "%s startup failed (%s); retry in 60 seconds.",
                            name,
                            type(exc).__name__,
                        )
                        next_attempt[name] = now + 60
            (path.parent / "status.json").write_text(
                json.dumps(
                    {
                        "updated_unix": time.time(),
                        "supervisor_pid": __import__("os").getpid(),
                        "components": {
                            name: {"pid": child.pid, "running": child.poll() is None}
                            for name, child in children.items()
                        },
                    }
                ),
                encoding="utf-8",
            )
            time.sleep(5)
    finally:
        for child in children.values():
            child.close()
        logger.info("Supervisor stopped; owned processes terminated.")
        kernel.CloseHandle(mutex)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.config.absolute()
    if args.check:
        load_config(path)
        print("Production paths and required configuration verified; secrets omitted.")
        return
    if sys.platform != "win32":
        raise SystemExit("Use the Windows boot task for this deployment.")
    supervise(path)


if __name__ == "__main__":
    main()
