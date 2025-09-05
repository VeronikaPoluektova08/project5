import bcrypt
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

def encrypt_message(message: str) -> bytes:
    key = load_key()
    f = Fernet(key)
    return f.encrypt(message.encode())

def decrypt_message(token: bytes) -> str:
    key = load_key()
    f = Fernet(key)
    return f.decrypt(token).decode()
