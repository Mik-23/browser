import base64
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


load_dotenv()


def gen_key(id, salt):
    kdf = Scrypt(salt=salt.encode('utf-8'), length=32, n=2**14, r=8, p=1)
    key = kdf.derive(str(id).encode())
    return base64.urlsafe_b64encode(key)


def encrypt_text(text, key):
    fer = Fernet(key)
    encrypt_data = fer.encrypt(text.encode('utf-8'))
    return encrypt_data


def decrypt_text(text, key):
    fer = Fernet(key)
    decrypt_data = fer.decrypt(text)
    return decrypt_data


def encrypt_file(file_path, key):
    fer = Fernet(key)

    with open(file_path, 'rb') as f:
        data = f.read()

    encrypt_data = fer.encrypt(data)

    with open(file_path, 'wb') as f:
        f.write(encrypt_data)


def decrypt_file(file_path, key):
    fer = Fernet(key)

    with open(file_path, 'rb') as f:
        data = f.read()
    decrypt_data = fer.decrypt(data)

    with open(file_path, 'wb') as f:
        f.write(decrypt_data)
