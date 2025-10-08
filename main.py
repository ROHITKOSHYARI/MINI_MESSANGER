# main.py
from keys import generate_rsa_keypair, rsa_private_to_pem, rsa_public_to_pem
from hybrid import hybrid_encrypt, hybrid_decrypt

# 1️⃣ Generate keys for Alice & Bob
alice_priv, alice_pub = generate_rsa_keypair()
bob_priv, bob_pub = generate_rsa_keypair()

alice_priv_pem = rsa_private_to_pem(alice_priv)
alice_pub_pem = rsa_public_to_pem(alice_pub)
bob_priv_pem = rsa_private_to_pem(bob_priv)
bob_pub_pem = rsa_public_to_pem(bob_pub)

print("=== Secure Messenger Demo ===")
print("Type 'exit' to quit.\n")

while True:
    # 2️⃣ Alice sends message to Bob
    message = input("Alice → Bob: ")
    if message.lower() == "exit":
        break

    # Encrypt the message
    bundle = hybrid_encrypt(
        message.encode("utf-8"),
        recipient_pub_pem=bob_pub_pem,
        sender_priv_pem=alice_priv_pem,
        sender_id="Alice"
    )
    print("\n[Encrypted Bundle Sent]\n", bundle, "\n")

    # Bob receives and decrypts
    decrypted = hybrid_decrypt(bundle, recipient_priv_pem=bob_priv_pem, sender_pub_pem=alice_pub_pem)
    print("Bob receives (Decrypted):", decrypted.decode("utf-8"), "\n")

    # 3️⃣ Optional: Bob replies to Alice
    reply = input("Bob → Alice: ")
    if reply.lower() == "exit":
        break

    reply_bundle = hybrid_encrypt(
        reply.encode("utf-8"),
        recipient_pub_pem=alice_pub_pem,
        sender_priv_pem=bob_priv_pem,
        sender_id="Bob"
    )
    print("\n[Encrypted Bundle Sent]\n", reply_bundle, "\n")

    decrypted_reply = hybrid_decrypt(reply_bundle, recipient_priv_pem=alice_priv_pem, sender_pub_pem=bob_pub_pem)
    print("Alice receives (Decrypted):", decrypted_reply.decode("utf-8"), "\n")
