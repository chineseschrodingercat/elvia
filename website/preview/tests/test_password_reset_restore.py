"""Restoring a private snapshot must not revive an old password reset link."""
import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[2] / 'ops/workspace_backup.py'
spec = importlib.util.spec_from_file_location('reset_backup_helper', HELPER)
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class ResetRecoveryTest(unittest.TestCase):
    def test_restore_expires_reset_links_and_preserves_durable_identity(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            source = root / 'synthetic-state'
            source.mkdir()
            with closing(sqlite3.connect(source / 'elvia.sqlite3')) as db:
                db.executescript('''
                    CREATE TABLE users(id TEXT PRIMARY KEY, role TEXT NOT NULL);
                    INSERT INTO users VALUES('synthetic-user','maintainer');
                    CREATE TABLE google_identities(subject TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id));
                    INSERT INTO google_identities VALUES('synthetic-subject','synthetic-user');
                    CREATE TABLE password_reset_tokens(token_hash TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id));
                    INSERT INTO password_reset_tokens VALUES('synthetic-digest','synthetic-user');
                    CREATE TABLE sessions(token TEXT); INSERT INTO sessions VALUES('synthetic-session');
                    CREATE TABLE email_challenges(challenge TEXT); INSERT INTO email_challenges VALUES('synthetic-code');
                    CREATE TABLE oauth_states(state_hash TEXT); INSERT INTO oauth_states VALUES('synthetic-state');
                ''')
            snapshot, restored = root / 'snapshot', root / 'restored'
            backup.snapshot(source, snapshot, True)
            backup.restore(snapshot, restored)
            with closing(sqlite3.connect(restored / 'elvia.sqlite3')) as db:
                self.assertEqual(db.execute('SELECT role FROM users').fetchall(), [('maintainer',)])
                self.assertEqual(db.execute('SELECT COUNT(*) FROM google_identities').fetchone()[0], 1)
                for table in ('sessions', 'email_challenges', 'oauth_states', 'password_reset_tokens'):
                    self.assertEqual(db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0], 0, table)
            for preserved in (source, snapshot):
                with closing(sqlite3.connect(preserved / 'elvia.sqlite3')) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
