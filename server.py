from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from hybrid import hybrid_encrypt, hybrid_decrypt
from keys import generate_rsa_keypair, rsa_private_to_pem, rsa_public_to_pem

app = FastAPI()

# Generate keys
alice_priv, alice_pub = generate_rsa_keypair()
bob_priv, bob_pub = generate_rsa_keypair()

def regenerate_keys():
    global alice_priv, alice_pub, bob_priv, bob_pub
    alice_priv, alice_pub = generate_rsa_keypair()
    bob_priv, bob_pub = generate_rsa_keypair()

# Request Model
class SendRequest(BaseModel):
    sender: str
    plaintext: str

@app.post("/api/send")
def send_message(req: SendRequest):

    text = req.plaintext.encode()

    if req.sender == "alice":
        sender_priv = alice_priv
        recipient_pub = bob_pub
        recipient_priv = bob_priv
    elif req.sender == "bob":
        sender_priv = bob_priv
        recipient_pub = alice_pub
        recipient_priv = alice_priv
    else:
        return {"error": "Invalid sender"}

    bundle_json = hybrid_encrypt(
        text,
        rsa_public_to_pem(recipient_pub),
        rsa_private_to_pem(sender_priv),
        req.sender.capitalize()
    )

    decrypted = hybrid_decrypt(
        bundle_json,
        rsa_private_to_pem(recipient_priv),
        None
    ).decode()

    return {
        "bundle": bundle_json,
        "decrypted": decrypted,
        "from": req.sender
    }

@app.post("/api/regenerate-keys")
def regen_keys():
    regenerate_keys()
    return {"status": "keys regenerated"}

@app.get("/api/keys")
def get_keys():
    return {
        "alice_pub": rsa_public_to_pem(alice_pub).decode(),
        "alice_priv": rsa_private_to_pem(alice_priv).decode(),
        "bob_pub": rsa_public_to_pem(bob_pub).decode(),
        "bob_priv": rsa_private_to_pem(bob_priv).decode()
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
