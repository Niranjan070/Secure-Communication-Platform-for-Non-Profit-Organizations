import base64
import hashlib
import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("utf-8")


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("utf-8"))


def _wrap_key(secret: str) -> bytes:
    """Derive a 256-bit wrapping key from the app secret."""
    return hashlib.sha256(secret.encode("utf-8")).digest()


def generate_rsa_key_pair() -> tuple[str, str]:
    """Create a per-user RSA key pair for encryption and signatures."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return public_pem, private_pem


def wrap_private_key(private_pem: str, secret: str) -> dict:
    """Encrypt the server-side copy of the private key for demo safety."""
    aesgcm = AESGCM(_wrap_key(secret))
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, private_pem.encode("utf-8"), None)
    return {"nonce": _b64encode(nonce), "ciphertext": _b64encode(ciphertext)}


def unwrap_private_key(wrapped_private_key: dict, secret: str) -> bytes:
    aesgcm = AESGCM(_wrap_key(secret))
    private_pem = aesgcm.decrypt(
        _b64decode(wrapped_private_key["nonce"]),
        _b64decode(wrapped_private_key["ciphertext"]),
        None,
    )
    return private_pem


def load_public_key(public_pem: str):
    return serialization.load_pem_public_key(public_pem.encode("utf-8"))


def load_private_key(private_pem: bytes):
    return serialization.load_pem_private_key(private_pem, password=None)


def generate_aes_key() -> bytes:
    return os.urandom(32)


def encrypt_with_aes(plaintext: bytes, aes_key: bytes) -> tuple[bytes, bytes]:
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce, ciphertext


def decrypt_with_aes(nonce: bytes, ciphertext: bytes, aes_key: bytes) -> bytes:
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def rsa_encrypt_key(aes_key: bytes, public_pem: str) -> str:
    public_key = load_public_key(public_pem)
    ciphertext = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return _b64encode(ciphertext)


def rsa_decrypt_key(encrypted_key: str, private_pem: bytes) -> bytes:
    private_key = load_private_key(private_pem)
    return private_key.decrypt(
        _b64decode(encrypted_key),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def encrypt_for_sender_and_recipient(
    plaintext: bytes, sender_public_pem: str, recipient_public_pem: str
) -> dict:
    """Encrypt a payload once with AES, then wrap the AES key for both parties."""
    aes_key = generate_aes_key()
    nonce, ciphertext = encrypt_with_aes(plaintext, aes_key)
    return {
        "nonce_b64": _b64encode(nonce),
        "ciphertext_b64": _b64encode(ciphertext),
        "ciphertext_bytes": ciphertext,
        "encrypted_key_sender": rsa_encrypt_key(aes_key, sender_public_pem),
        "encrypted_key_recipient": rsa_encrypt_key(aes_key, recipient_public_pem),
    }


def decrypt_for_viewer(
    nonce: bytes, ciphertext: bytes, encrypted_key: str, private_pem: bytes
) -> bytes:
    aes_key = rsa_decrypt_key(encrypted_key, private_pem)
    return decrypt_with_aes(nonce, ciphertext, aes_key)


def sign_blob(private_pem: bytes, payload: bytes) -> str:
    private_key = load_private_key(private_pem)
    signature = private_key.sign(
        payload,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return _b64encode(signature)


def verify_signature(public_pem: str, payload: bytes, signature: str) -> bool:
    public_key = load_public_key(public_pem)
    try:
        public_key.verify(
            _b64decode(signature),
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
