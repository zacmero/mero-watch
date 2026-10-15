import asyncio
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch
from contextlib import redirect_stdout

from scripts.watch_ota import failure_record, status_description, run


class OTADiagnosticsTests(unittest.TestCase):
    def test_device_result_decode_is_specific_to_e6(self):
        self.assertEqual(status_description(b'\x04'), 'bad update file')
        self.assertIn('relink', status_description(b'\x80'))
        self.assertEqual(status_description(b''), 'empty device result')
        self.assertEqual(status_description(b'\xff'), 'unknown device result')

    def test_failure_keeps_stage_and_exact_last_range_without_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(log=Path(directory) / 'events.jsonl')
            rows = [dict(event='selected', sha256='test', address='loader'),
                    dict(event='pass_two_loader_confirmed'),
                    dict(event='block_requested', offset=4096, length=512),
                    dict(event='transfer_done_status', status='04',
                         status_description='bad update file', blocks=344)]
            args.log.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            record = failure_record(args, RuntimeError('private auth payload'))
            self.assertEqual(record['context']['stage'], 'mandatory_loader')
            self.assertEqual(record['context']['offset'], 4096)
            self.assertEqual(record['context']['length'], 512)
            self.assertEqual(record['context']['status'], '04')
            self.assertNotIn('private auth', json.dumps(record))
            self.assertEqual(record['event'], 'update_failed')
            rows[-1]['status'] = '80'
            args.log.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            self.assertEqual(failure_record(args, RuntimeError())['event'], 'handoff_pending')

    def test_connection_failure_is_journaled_and_rethrown(self):
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(log=Path(directory) / 'events.jsonl')
            with patch('scripts.watch_ota._run', new=AsyncMock(side_effect=ConnectionError('secret'))):
                with redirect_stdout(io.StringIO()), self.assertRaises(ConnectionError):
                    asyncio.run(run(args))
            record = json.loads(args.log.read_text())
            self.assertEqual(record['exception_type'], 'ConnectionError')
            self.assertEqual(record['event'], 'update_failed')
            self.assertNotIn('secret', args.log.read_text())
            self.assertEqual(args.log.stat().st_mode & 0o777, 0o600)
