import json, os, base64
from datetime import datetime, timezone

from keys import load_private_pem, load_public_pem
from rsa_utils import rsa_encrypt_public, rsa_decrypt_private, sign_with_rsa_private, verify_rsa_signature
from aes_utils import aes_gcm_encrypt, aes_gcm_decrypt

def b64(x: bytes) -> str:
    return base64.b64encode(x).decode('ascii')

def ub64(s: str) -> bytes:
    return base64.b64decode(s.encode('ascii'))

def hybrid_encrypt(plaintext: bytes, recipient_pub_pem: bytes, sender_priv_pem: bytes = None, sender_id: str = "") -> str:

    recipient_pub = load_public_pem(recipient_pub_pem)
    session_key = os.urandom(32)

    iv, ct, tag = aes_gcm_encrypt(session_key, plaintext)

    enc_session = rsa_encrypt_public(recipient_pub, session_key)

    timestamp = datetime.now(timezone.utc).isoformat()

    bundle = {
        "sender_id": sender_id,
        "timestamp": timestamp,
        "enc_session_key": b64(enc_session),
        "iv": b64(iv),
        "ciphertext": b64(ct),
        "tag": b64(tag),
        "signature": None
    }

    if sender_priv_pem:
        sender_priv = load_private_pem(sender_priv_pem)
        to_sign = (bundle["enc_session_key"] + bundle["iv"] + bundle["ciphertext"] + timestamp).encode()
        sig = sign_with_rsa_private(sender_priv, to_sign)
        bundle["signature"] = b64(sig)

    return json.dumps(bundle)

def hybrid_decrypt(bundle_json: str, recipient_priv_pem: bytes, sender_pub_pem: bytes = None):

    bundle = json.loads(bundle_json)

    recipient_priv = load_private_pem(recipient_priv_pem)

    enc_session = ub64(bundle["enc_session_key"])
    iv = ub64(bundle["iv"])
    ciphertext = ub64(bundle["ciphertext"])
    tag = ub64(bundle["tag"])

    session_key = rsa_decrypt_private(recipient_priv, enc_session)

    if bundle.get("signature") and sender_pub_pem:
        to_sign = (bundle["enc_session_key"] + bundle["iv"] + bundle["ciphertext"] + bundle["timestamp"]).encode()
        sender_pub = load_public_pem(sender_pub_pem)
        if not verify_rsa_signature(sender_pub, to_sign, ub64(bundle["signature"])):
            raise ValueError("Signature verification failed")

    plaintext = aes_gcm_decrypt(session_key, iv, ciphertext, tag)
    return plaintext
