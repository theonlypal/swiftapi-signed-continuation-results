"""Offline checks for archive paths, pinned bytes and SDK signature rejection."""
from pathlib import Path
import tempfile
import unittest
import json
from nacl.exceptions import BadSignatureError

import verify


class EvidenceVerifierTests(unittest.TestCase):
    def test_relative_paths(self):
        self.assertEqual(str(verify.safe_name('receipts/0000-VALID/receipt.json')),
                         'receipts/0000-VALID/receipt.json')

    def test_unsafe_paths_rejected(self):
        for name in ('../outside', '/absolute', 'a/../b', 'a\\b', './a', ''):
            with self.subTest(name=name), self.assertRaises(ValueError):
                verify.safe_name(name)

    def test_archive_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'evidence.tar.gz'
            archive.write_bytes(b'not evidence')
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                verify.extract_archive(archive, root, {'bytes': 12, 'sha256': '0' * 64})

    def test_prediction_file_exact_hash(self):
        anchors = verify.read_json(verify.ROOT / 'TRUST_ANCHORS.json')
        parsed = verify.sealed_predictions(verify.ROOT / 'AUTHOR_PREDICTIONS.md', anchors)
        self.assertEqual(len(parsed['PRIMARY']), 11)
        self.assertEqual(parsed['SECONDARY']['VALID']['class_counts'], {'R': 188})
        with self.assertRaisesRegex(ValueError, 'seal mismatch'):
            verify.sealed_predictions(verify.ROOT / 'AUTHOR_PREDICTIONS.md',
                                      {**anchors, 'author_predictions_sha256': '0' * 64})

    def test_ledger_uses_canonical_configuration(self):
        root = verify.ROOT / 'runs/PRIMARY'
        config = verify.read_json(root / 'run-config.json')
        record = verify.verify_finalization(root, config, 11)
        self.assertNotEqual(verify.digest(root / 'run-config.json'), record['config_sha256'])
        with self.assertRaisesRegex(ValueError, 'configuration hash mismatch'):
            verify.verify_finalization(root, {**config, 'max_grant_age_seconds': 61}, 11)

    def test_runtime_signature_tamper_rejected(self):
        root = verify.ROOT / 'runs/PRIMARY/receipts/0000-VALID'
        envelope = verify.read_json(root / 'receipt.json')
        envelope['payload']['output'] = '5'
        anchors = verify.read_json(verify.ROOT / 'TRUST_ANCHORS.json')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'receipt.json'
            path.write_text(json.dumps(envelope))
            with self.assertRaises(BadSignatureError):
                verify.verify_receipt(path, anchors['runtime_public_keys']['PRIMARY'], verify.MODE,
                                      expected_max_grant_age_seconds=60)


if __name__ == '__main__':
    unittest.main()
