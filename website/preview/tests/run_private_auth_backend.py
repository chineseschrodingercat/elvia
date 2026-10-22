"""Guarded synthetic backend runner: no providers or active local listeners."""
import contextlib
import json
from pathlib import Path
import socket
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'preview'/'tests'), str(ROOT/'preview'/'server')]
original_connect, original_dns = socket.socket.connect, socket.getaddrinfo
blocked = []


def connect(self, address):
    if isinstance(address, tuple) and (address[0] not in ('127.0.0.1', '::1', 'localhost') or address[1] in (8797, 8799)):
        blocked.append('non-test destination')
        raise AssertionError('Provider connections and live ports 8797/8799 are blocked in synthetic QA')
    return original_connect(self, address)


def dns(host, *args, **kwargs):
    if host not in ('127.0.0.1', '::1', 'localhost', None):
        blocked.append('external DNS')
        raise AssertionError('External DNS is blocked in synthetic QA')
    return original_dns(host, *args, **kwargs)


socket.socket.connect, socket.getaddrinfo = connect, dns
label = sys.argv[1]
modules = sys.argv[2:] or ['test_private_origin']
destination = ROOT/'evidence'/'private-auth'
destination.mkdir(parents=True, exist_ok=True)
started = time.monotonic()
with (destination/('backend-'+label+'.log')).open('w', encoding='utf-8') as log:
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        suite = (unittest.defaultTestLoader.discover(str(ROOT/'preview'/'tests')) if modules == ['all']
                 else unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in modules))
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
report = {'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
          'skipped': len(result.skipped), 'success': result.wasSuccessful(),
          'seconds': round(time.monotonic()-started, 3), 'blocked_network_attempts': len(blocked),
          'live_data_used': False, 'real_mail_or_oauth': False}
(destination/('backend-'+label+'.json')).write_text(json.dumps(report, indent=2)+'\n', 'utf-8')
print(json.dumps(report))
if not result.wasSuccessful():
    # This runner permits synthetic fixtures only. Surface failure details in CI
    # instead of leaving the only actionable traceback in a runner-local file.
    for test, detail in result.failures + result.errors:
        print(f'FAILED: {test.id()}\n{detail}')
raise SystemExit(0 if result.wasSuccessful() else 1)
