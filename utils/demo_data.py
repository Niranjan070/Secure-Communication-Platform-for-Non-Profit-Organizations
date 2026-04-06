import json
import uuid
from datetime import datetime
from pathlib import Path

import bcrypt

from utils.crypto_utils import (
    encrypt_for_sender_and_recipient,
    generate_rsa_key_pair,
    sha256_hex,
    sign_blob,
    unwrap_private_key,
    wrap_private_key,
)
from utils.security_helpers import normalize_email


def _utc_now():
    return datetime.utcnow()


def _create_user(db, wrap_secret: str, full_name: str, email: str, password: str, role: str):
    normalized_email = normalize_email(email)
    existing = db.users.find_one({"email": normalized_email})
    if existing:
        return existing

    public_key_pem, private_key_pem = generate_rsa_key_pair()
    user = {
        "full_name": full_name,
        "email": normalized_email,
        "password_hash": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role": role,
        "public_key_pem": public_key_pem,
        "private_key_wrapped": wrap_private_key(private_key_pem, wrap_secret),
        "failed_login_count": 0,
        "created_at": _utc_now(),
    }
    inserted = db.users.insert_one(user)
    return db.users.find_one({"_id": inserted.inserted_id})


def _create_demo_message(db, wrap_secret: str, sender: dict, recipient: dict):
    existing = db.messages.find_one(
        {"sender_id": sender["_id"], "recipient_id": recipient["_id"], "demo_seed": True}
    )
    if existing:
        return existing

    payload = {
        "subject": "Shelter inventory update",
        "body": (
            "Solar lanterns and first-aid kits were moved to the secure storeroom. "
            "Please review the signed inventory sheet before tomorrow's field visit."
        ),
        "label": "PGP-style internal email",
        "created_at": _utc_now().isoformat(),
    }
    plaintext = json.dumps(payload, sort_keys=True).encode("utf-8")
    sender_private_key = unwrap_private_key(sender["private_key_wrapped"], wrap_secret)
    envelope = encrypt_for_sender_and_recipient(
        plaintext,
        sender["public_key_pem"],
        recipient["public_key_pem"],
    )
    message = {
        "sender_id": sender["_id"],
        "recipient_id": recipient["_id"],
        "signature": sign_blob(sender_private_key, plaintext),
        "encrypted_payload": {
            "nonce": envelope["nonce_b64"],
            "ciphertext": envelope["ciphertext_b64"],
            "encrypted_key_sender": envelope["encrypted_key_sender"],
            "encrypted_key_recipient": envelope["encrypted_key_recipient"],
        },
        "message_type": "secure_email",
        "demo_seed": True,
        "created_at": _utc_now(),
    }
    inserted = db.messages.insert_one(message)
    return db.messages.find_one({"_id": inserted.inserted_id})


def _create_demo_file(db, wrap_secret: str, upload_folder: str, sender: dict, recipient: dict):
    existing = db.secure_files.find_one(
        {"sender_id": sender["_id"], "recipient_id": recipient["_id"], "demo_seed": True}
    )
    if existing:
        return existing

    sample_path = Path(__file__).resolve().parents[1] / "sample_data" / "demo-policy.pdf"
    file_bytes = sample_path.read_bytes()
    sender_private_key = unwrap_private_key(sender["private_key_wrapped"], wrap_secret)
    envelope = encrypt_for_sender_and_recipient(
        file_bytes,
        sender["public_key_pem"],
        recipient["public_key_pem"],
    )

    stored_filename = f"{uuid.uuid4().hex}.bin"
    output_path = Path(upload_folder) / stored_filename
    output_path.write_bytes(envelope["ciphertext_bytes"])

    file_record = {
        "sender_id": sender["_id"],
        "recipient_id": recipient["_id"],
        "original_filename": "demo-policy.pdf",
        "stored_filename": stored_filename,
        "mime_type": "application/pdf",
        "size": len(file_bytes),
        "sha256": sha256_hex(file_bytes),
        "signature": sign_blob(sender_private_key, file_bytes),
        "nonce": envelope["nonce_b64"],
        "encrypted_key_sender": envelope["encrypted_key_sender"],
        "encrypted_key_recipient": envelope["encrypted_key_recipient"],
        "ciphertext_preview": envelope["ciphertext_b64"][:120],
        "demo_seed": True,
        "created_at": _utc_now(),
    }
    inserted = db.secure_files.insert_one(file_record)
    return db.secure_files.find_one({"_id": inserted.inserted_id})


def seed_demo_data(db, wrap_secret: str, upload_folder: str) -> dict:
    """Create a reusable demo environment with two NGO users, a message, and a file."""
    admin = _create_user(
        db,
        wrap_secret,
        "Amina Rahman",
        "admin@ngo.local",
        "Admin@123",
        "Admin",
    )
    staff = _create_user(
        db,
        wrap_secret,
        "Daniel Kim",
        "staff@ngo.local",
        "Staff@123",
        "Staff",
    )
    message = _create_demo_message(db, wrap_secret, admin, staff)
    secure_file = _create_demo_file(db, wrap_secret, upload_folder, admin, staff)
    return {
        "admin_email": admin["email"],
        "staff_email": staff["email"],
        "message_id": str(message["_id"]),
        "file_id": str(secure_file["_id"]),
    }
