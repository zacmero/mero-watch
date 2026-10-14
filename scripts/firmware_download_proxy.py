"""Narrow mitmproxy addon serving an explicitly selected local firmware file.

Only the captured vendor POST download and optional restoration checksum are
replaced. No credentials, request bodies, keys or unrelated responses are logged. Launch via
mitmdump with watch_firmware and watch_firmware_sha256 options.
"""
import hashlib
import json
import base64
import builtins
import os
from pathlib import Path
from mitmproxy import ctx, http


def print(message, **kwargs):
    """Keep only this addon's sanitized events for installation evidence."""
    path = Path("captures/firmware-work/load-test-events.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as out:
        os.chmod(path, 0o600)
        out.write(json.dumps({"event": message}) + "\n")
    builtins.print(message, **kwargs)


def replace_metadata(body, key, md5):
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    envelope = json.loads(body)
    if str(envelope.get("code")) != "200":
        return body, False
    encoded = json.loads(envelope["data"])
    aes_key = key.decrypt(base64.b64decode(encoded["responStr1"]), rsa_padding.PKCS1v15())
    decryptor = Cipher(algorithms.AES(aes_key), modes.ECB()).decryptor()
    plain = decryptor.update(base64.b64decode(encoded["responStr2"])) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    metadata = json.loads(unpadder.update(plain) + unpadder.finalize())
    if (metadata.get("pid") != 76 or metadata.get("version") != 1004
            or metadata.get("fileMd5") != "550f4fcf32916da3a2dbb77c9510ee3e"):
        raise ValueError("Metadata does not identify the captured stock build")
    metadata["fileMd5"] = md5
    padder = padding.PKCS7(128).padder()
    plain = json.dumps(metadata, ensure_ascii=False, separators=(",", ":")).encode()
    padded = padder.update(plain) + padder.finalize()
    encryptor = Cipher(algorithms.AES(aes_key), modes.ECB()).encryptor()
    encoded["responStr2"] = base64.b64encode(encryptor.update(padded) + encryptor.finalize()).decode()
    envelope["data"] = json.dumps(encoded, separators=(",", ":"))
    return json.dumps(envelope, ensure_ascii=False, separators=(",", ":")).encode(), True


class FirmwareDownloadProxy:
    def load(self, loader):
        loader.add_option("watch_firmware", str, "", "Local UFW to supply")
        loader.add_option("watch_firmware_sha256", str, "", "Required file SHA256")
        loader.add_option("watch_crypto_source", str, "", "Private inspected app disassembly JSON")

    def configure(self, updated):
        if not ctx.options.watch_firmware or not ctx.options.watch_firmware_sha256:
            self.payload = None
            return
        payload = Path(ctx.options.watch_firmware).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != ctx.options.watch_firmware_sha256:
            raise ValueError("Selected firmware SHA256 mismatch")
        self.payload = payload
        self.digest = digest
        self.key = None
        if ctx.options.watch_crypto_source:
            from cryptography.hazmat.primitives import serialization
            classes = json.loads(Path(ctx.options.watch_crypto_source).read_text())
            value = next(f["value"] for c in classes for f in c["fields"]
                         if f["name"] == "PRIVATE_REDATA")
            self.key = serialization.load_der_private_key(base64.b64decode(value.strip('"')), None)

    def request(self, flow):
        path = flow.request.path.split("?", 1)[0]
        if flow.request.host.endswith("gssdfit.com") or flow.request.host == "mitm.it":
            print("PROXY_REQUEST " + json.dumps({"host": flow.request.host,
                  "path": path, "method": flow.request.method}), flush=True)
        if (flow.request.host == "awsapp.gssdfit.com"
                and flow.request.method == "POST"
                and path == "/abroad/awsd/ota/piddownload"):
            if not self.payload:
                flow.response = http.Response.make(503, b"Firmware not selected")
                return
            flow.response = http.Response.make(200, self.payload, {
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(self.payload)),
                "Cache-Control": "no-store",
            })
            print("LOCAL_FIRMWARE_SERVED " + json.dumps({
                "bytes": len(self.payload), "sha256": self.digest}), flush=True)

    def response(self, flow):
        path = flow.request.path.split("?", 1)[0]
        if (flow.request.host == "awsapp.gssdfit.com"
                and path.startswith("/abroad/awsd/ota/")):
            if path == "/abroad/awsd/ota/userUpgradeOta" and self.key:
                try:
                    body, changed = replace_metadata(flow.response.content, self.key,
                                                     hashlib.md5(self.payload).hexdigest())
                    flow.response.content = body
                    if changed:
                        print("MODIFIED_FIRMWARE_METADATA_READY", flush=True)
                except Exception:
                    flow.response = http.Response.make(502, b"Firmware metadata validation failed")
                    print("FIRMWARE_METADATA_REJECTED", flush=True)
            code = None
            try:
                code = json.loads(flow.response.content).get("code")
            except (ValueError, AttributeError):
                pass
            print("OTA_RESPONSE " + json.dumps({"path": path,
                  "status": flow.response.status_code,
                  "code": code, "bytes": len(flow.response.content or b"")}), flush=True)

    def tls_failed_client(self, data):
        print("PROXY_TLS_CLIENT_FAILED", flush=True)

    def error(self, flow):
        print("PROXY_FLOW_FAILED " + json.dumps({"host": flow.request.host}), flush=True)


addons = [FirmwareDownloadProxy()]
