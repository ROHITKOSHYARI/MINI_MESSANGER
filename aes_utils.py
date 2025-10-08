# aes_utils.py
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def aes_gcm_encrypt(key: bytes, plaintext: bytes, aad: bytes = None):
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, aad)
    tag = ciphertext[-16:]
    ct = ciphertext[:-16]
    return iv, ct, tag

def aes_gcm_decrypt(key: bytes, iv: bytes, ciphertext: bytes, tag: bytes, aad: bytes = None):
    aesgcm = AESGCM(key)
    ct_with_tag = ciphertext + tag
    return aesgcm.decrypt(iv, ct_with_tag, aad)
