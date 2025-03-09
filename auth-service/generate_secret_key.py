import secrets

def generate_secret_key(length=32):
    return secrets.token_hex(length)

# Generate a 32-byte secret key
secret_key = generate_secret_key()
print(f"Your secret key: {secret_key}")