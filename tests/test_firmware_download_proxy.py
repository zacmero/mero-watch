"""Run in the optional mitmproxy environment; no vendor keys or images needed."""
import base64
import json
import unittest

try:
    from scripts.firmware_download_proxy import replace_metadata
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:
    replace_metadata = None


@unittest.skipIf(replace_metadata is None, "optional proxy dependencies unavailable")
class MetadataRewriteTests(unittest.TestCase):
    def setUp(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
        self.aes = b"synthetic-test-k"
        self.metadata = dict(pid=76, version=1004,
                             fileMd5="550f4fcf32916da3a2dbb77c9510ee3e",
                             fwareName="update1004.ufw", fwareSize=18320)

    def envelope(self, metadata):
        padder = padding.PKCS7(128).padder()
        payload = json.dumps(metadata).encode()
        padded = padder.update(payload) + padder.finalize()
        encryptor = Cipher(algorithms.AES(self.aes), modes.ECB()).encryptor()
        wrapped = dict(responStr1=base64.b64encode(self.key.public_key().encrypt(
            self.aes, rsa_padding.PKCS1v15())).decode(),
            responStr2=base64.b64encode(encryptor.update(padded) + encryptor.finalize()).decode())
        return json.dumps(dict(code="200", data=json.dumps(wrapped))).encode()

    def test_only_download_checksum_changes(self):
        original = self.envelope(self.metadata)
        result, changed = replace_metadata(original, self.key, "a" * 32)
        self.assertTrue(changed)
        wrapped = json.loads(json.loads(result)["data"])
        self.assertEqual(wrapped["responStr1"], json.loads(json.loads(original)["data"])["responStr1"])
        decryptor = Cipher(algorithms.AES(self.aes), modes.ECB()).decryptor()
        plain = decryptor.update(base64.b64decode(wrapped["responStr2"])) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        decoded = json.loads(unpadder.update(plain) + unpadder.finalize())
        self.assertEqual(decoded, dict(self.metadata, fileMd5="a" * 32))

    def test_other_device_is_rejected(self):
        with self.assertRaises(ValueError):
            replace_metadata(self.envelope(dict(self.metadata, pid=77)), self.key, "a" * 32)

    def test_error_response_is_preserved(self):
        body = b'{"code":"1024"}'
        self.assertEqual(replace_metadata(body, self.key, "a" * 32), (body, False))
