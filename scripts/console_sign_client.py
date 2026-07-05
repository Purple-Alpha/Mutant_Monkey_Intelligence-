#!/usr/bin/env python3
"""
Operator sign client — validate bundle, sign manifest, POST sign (private key stays local).

Lab helper only. Production: use your own isolated signer with matt-ed25519-01 key material.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_CONSOLE = "http://127.0.0.1:8767"
DEFAULT_PUBKEY_INSTALL = Path("/tmp/mmi_console_server/keys/operator_ed25519.pub")


def _post_json(url: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"error": body}


def _get_json(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"error": body}


def generate_lab_keys(key_dir: Path) -> tuple[Path, Path]:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key_dir.mkdir(parents=True, exist_ok=True)
    priv_path = key_dir / "operator_ed25519.priv"
    pub_path = key_dir / "operator_ed25519.pub"
    priv = Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes_raw()
    pub_bytes = priv.public_key().public_bytes_raw()
    priv_path.write_bytes(priv_bytes)
    pub_path.write_bytes(pub_bytes)
    priv_path.chmod(0o600)
    return priv_path, pub_path


def install_pubkey(pub_path: Path, dest: Path = DEFAULT_PUBKEY_INSTALL) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pub_path.read_bytes())


def sign_flow(
    bundle: dict,
    *,
    console_base: str,
    private_key_path: Path,
    operator_key_id: str = "matt-ed25519-01",
) -> dict:
    authority = Path(__file__).resolve().parents[1]
    chaos = authority / "mmi/project_brain/chaos"
    if str(chaos) not in sys.path:
        sys.path.insert(0, str(chaos))
    from console_evidence_gate import manifest_bytes, manifest_hash  # type: ignore
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    base = console_base.rstrip("/")
    status, validate_resp = _post_json(f"{base}/api/v1/evidence-bundle/validate", bundle)
    if validate_resp.get("verdict") != "VALID":
        return {"step": "validate", "status": status, "response": validate_resp}

    bundle_id = validate_resp["bundle_id"]
    status, review = _get_json(f"{base}/api/v1/evidence-bundle/{bundle_id}")
    if status != 200:
        return {"step": "review", "status": status, "response": review}

    manifest = review["manifest_fields"]
    signed_at_ms = int(time.time() * 1000)
    manifest["signed_at_ms"] = signed_at_ms
    mh = manifest_hash(manifest)

    priv = Ed25519PrivateKey.from_private_bytes(private_key_path.read_bytes())
    sig = base64.b64encode(priv.sign(manifest_bytes(manifest))).decode("ascii")

    sign_req = {
        "bundle_id": bundle_id,
        "sign_seq": review["next_sign_seq"],
        "signed_at_ms": signed_at_ms,
        "manifest_hash": mh,
        "signature_b64": sig,
        "operator_key_id": operator_key_id,
    }
    status, sign_resp = _post_json(f"{base}/api/v1/evidence-bundle/sign", sign_req)
    return {"step": "sign", "status": status, "validate": validate_resp, "sign_request": sign_req, "response": sign_resp}


def main() -> int:
    parser = argparse.ArgumentParser(description="MMI console operator sign client")
    parser.add_argument("--console", default=DEFAULT_CONSOLE)
    parser.add_argument("--bundle", type=Path, help="console_evidence_v1 bundle JSON")
    parser.add_argument("--private-key", type=Path, help="raw 32-byte Ed25519 private key file")
    parser.add_argument("--generate-lab-keys", type=Path, metavar="KEY_DIR")
    parser.add_argument("--install-pubkey", type=Path, metavar="PUB_PATH")
    parser.add_argument("--operator-key-id", default="matt-ed25519-01")
    parser.add_argument("--health", action="store_true", help="GET /api/v1/health only")
    args = parser.parse_args()

    if args.generate_lab_keys:
        priv, pub = generate_lab_keys(args.generate_lab_keys)
        print(json.dumps({"private_key": priv.as_posix(), "public_key": pub.as_posix()}, indent=2))
        print(
            f"\nInstall pubkey for server:\n"
            f"  python3 scripts/console_sign_client.py --install-pubkey {pub.as_posix()}",
            file=sys.stderr,
        )
        return 0

    if args.install_pubkey:
        install_pubkey(args.install_pubkey)
        print(json.dumps({"verdict": "INSTALLED", "path": DEFAULT_PUBKEY_INSTALL.as_posix()}))
        return 0

    if args.health:
        status, body = _get_json(f"{args.console.rstrip('/')}/api/v1/health")
        print(json.dumps(body, indent=2))
        return 0 if status == 200 else 1

    if not args.bundle or not args.private_key:
        parser.error("--bundle and --private-key required (or use --generate-lab-keys / --health)")

    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    result = sign_flow(
        bundle,
        console_base=args.console,
        private_key_path=args.private_key,
        operator_key_id=args.operator_key_id,
    )
    print(json.dumps(result, indent=2))
    if result.get("response", {}).get("verdict") == "ACCEPTED":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
