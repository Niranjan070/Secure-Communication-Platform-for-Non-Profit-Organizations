import argparse
import base64
import json
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO

import bcrypt
from bson import ObjectId
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

from database.db import init_indexes, mongo
from utils.crypto_utils import (
    decrypt_for_viewer,
    encrypt_for_sender_and_recipient,
    generate_rsa_key_pair,
    sha256_hex,
    sign_blob,
    unwrap_private_key,
    verify_signature,
    wrap_private_key,
)
from utils.demo_data import seed_demo_data
from utils.security_helpers import (
    allowed_file,
    clean_text,
    human_size,
    is_valid_email,
    normalize_email,
    password_meets_policy,
    short_ciphertext,
    to_object_id,
)
from utils.theory_content import ACCESS_CONTROL_MATRIX, SECURITY_CONCEPTS

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "change-this-flask-secret")
app.config["PRIVATE_KEY_WRAP_SECRET"] = os.getenv(
    "PRIVATE_KEY_WRAP_SECRET",
    "change-this-private-key-wrap-secret",
)
app.config["MONGO_URI"] = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017/secure_ngo_platform",
)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=45)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("ENABLE_HTTPS_ONLY", "false").lower() == "true"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
mongo.init_app(app)
csrf = CSRFProtect(app)

with app.app_context():
    init_indexes()


def utc_now():
    return datetime.utcnow()


def current_user():
    user_id = session.get("user_id")
    object_id = to_object_id(user_id)
    if not object_id:
        return None
    return mongo.db.users.find_one({"_id": object_id})


@app.before_request
def load_current_user():
    session.permanent = True
    g.current_user = current_user()


@app.context_processor
def inject_current_user():
    return {"current_user": g.get("current_user")}


@app.template_filter("datetime_utc")
def datetime_utc(value):
    if not value:
        return "N/A"
    return value.strftime("%d %b %Y %H:%M UTC")


@app.template_filter("human_size")
def human_size_filter(value):
    return human_size(value or 0)


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not g.current_user:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not g.current_user:
                flash("Please sign in to continue.", "warning")
                return redirect(url_for("login"))
            if g.current_user["role"] not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


def log_activity(action: str, details: dict, severity: str = "info", user_id=None):
    mongo.db.activity_logs.insert_one(
        {
            "user_id": user_id if isinstance(user_id, ObjectId) else to_object_id(str(user_id or "")),
            "action": action,
            "details": details,
            "severity": severity,
            "created_at": utc_now(),
        }
    )


def get_user_private_key(user: dict) -> bytes:
    return unwrap_private_key(user["private_key_wrapped"], app.config["PRIVATE_KEY_WRAP_SECRET"])


def create_user_account(full_name: str, email: str, password: str, role: str) -> dict:
    public_key_pem, private_key_pem = generate_rsa_key_pair()
    user_document = {
        "full_name": full_name,
        "email": normalize_email(email),
        "password_hash": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role": role,
        "public_key_pem": public_key_pem,
        "private_key_wrapped": wrap_private_key(
            private_key_pem, app.config["PRIVATE_KEY_WRAP_SECRET"]
        ),
        "failed_login_count": 0,
        "created_at": utc_now(),
    }
    inserted = mongo.db.users.insert_one(user_document)
    return mongo.db.users.find_one({"_id": inserted.inserted_id})


def update_failed_login(email: str):
    user = mongo.db.users.find_one({"email": normalize_email(email)})
    if not user:
        log_activity("failed_login_unknown_user", {"email": normalize_email(email)}, "warning")
        return 0

    failed_count = user.get("failed_login_count", 0) + 1
    mongo.db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"failed_login_count": failed_count, "last_failed_login": utc_now()}},
    )
    severity = "warning" if failed_count >= 3 else "info"
    log_activity(
        "failed_login",
        {"email": user["email"], "failed_count": failed_count},
        severity,
        user["_id"],
    )
    return failed_count


def reset_failed_login(user_id: ObjectId):
    mongo.db.users.update_one(
        {"_id": user_id},
        {"$set": {"failed_login_count": 0, "last_successful_login": utc_now()}},
    )


def build_user_lookup():
    return {user["_id"]: user["full_name"] for user in mongo.db.users.find({}, {"full_name": 1})}


def can_access_record(record: dict, user_id: ObjectId) -> bool:
    return record["sender_id"] == user_id or record["recipient_id"] == user_id


def decrypt_message_payload(message: dict, viewer: dict):
    private_key = get_user_private_key(viewer)
    encrypted_key = (
        message["encrypted_payload"]["encrypted_key_sender"]
        if message["sender_id"] == viewer["_id"]
        else message["encrypted_payload"]["encrypted_key_recipient"]
    )
    plaintext = decrypt_for_viewer(
        nonce=base64.b64decode(message["encrypted_payload"]["nonce"]),
        ciphertext=base64.b64decode(message["encrypted_payload"]["ciphertext"]),
        encrypted_key=encrypted_key,
        private_pem=private_key,
    )
    return plaintext


def message_to_view_model(message: dict, viewer: dict, user_lookup: dict) -> dict:
    sender = mongo.db.users.find_one({"_id": message["sender_id"]}, {"public_key_pem": 1, "full_name": 1})
    try:
        plaintext = decrypt_message_payload(message, viewer)
        payload = json.loads(plaintext.decode("utf-8"))
        signature_valid = verify_signature(sender["public_key_pem"], plaintext, message["signature"])
    except Exception:
        payload = {"subject": "[Decryption failed]", "body": "The encrypted payload could not be recovered."}
        signature_valid = False

    return {
        "id": str(message["_id"]),
        "direction": "Sent" if message["sender_id"] == viewer["_id"] else "Received",
        "counterparty": user_lookup.get(
            message["recipient_id"] if message["sender_id"] == viewer["_id"] else message["sender_id"],
            "Unknown user",
        ),
        "subject": payload.get("subject", "(No subject)"),
        "body": payload.get("body", ""),
        "message_type": message.get("message_type", "secure_email"),
        "signature_valid": signature_valid,
        "created_at": message["created_at"],
        "sender_name": sender["full_name"],
        "encrypted_payload": message["encrypted_payload"],
    }


def file_to_view_model(file_record: dict, viewer: dict, user_lookup: dict) -> dict:
    return {
        "id": str(file_record["_id"]),
        "direction": "Sent" if file_record["sender_id"] == viewer["_id"] else "Received",
        "counterparty": user_lookup.get(
            file_record["recipient_id"]
            if file_record["sender_id"] == viewer["_id"]
            else file_record["sender_id"],
            "Unknown user",
        ),
        "original_filename": file_record["original_filename"],
        "mime_type": file_record["mime_type"],
        "size": file_record["size"],
        "sha256": file_record["sha256"],
        "created_at": file_record["created_at"],
        "ciphertext_preview": file_record.get("ciphertext_preview", ""),
    }


@app.route("/")
def index():
    if g.current_user:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    can_assign_admin = bool(g.current_user and g.current_user["role"] == "Admin")
    if request.method == "POST":
        full_name = clean_text(request.form.get("full_name"), 80)
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        role = request.form.get("role", "Staff")
        if not can_assign_admin:
            role = "Staff"

        if len(full_name) < 3:
            flash("Full name must be at least 3 characters long.", "danger")
        elif not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
        elif not password_meets_policy(password):
            flash(
                "Password must be at least 8 characters and include uppercase, lowercase, and a number.",
                "danger",
            )
        elif mongo.db.users.find_one({"email": email}):
            flash("That email is already registered.", "danger")
        else:
            user = create_user_account(full_name, email, password, role)
            log_activity("user_registered", {"email": user["email"], "role": role}, user_id=user["_id"])
            if not g.current_user:
                session["user_id"] = str(user["_id"])
                flash("Registration complete. Your RSA keys were generated securely.", "success")
                return redirect(url_for("dashboard"))
            flash(f"{role} account created for {user['full_name']}.", "success")
            return redirect(url_for("admin_panel"))

    return render_template("register.html", can_assign_admin=can_assign_admin)


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.current_user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        user = mongo.db.users.find_one({"email": email})

        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            failed_count = update_failed_login(email)
            flash("Invalid email or password.", "danger")
            if failed_count >= 3:
                flash("Alert: multiple failed login attempts were detected for this account.", "warning")
            return render_template("login.html")

        previous_failed_count = user.get("failed_login_count", 0)
        reset_failed_login(user["_id"])
        session.clear()
        session["user_id"] = str(user["_id"])
        log_activity("successful_login", {"email": user["email"]}, user_id=user["_id"])
        if previous_failed_count >= 3:
            flash("Warning: this account recently had multiple failed login attempts.", "warning")
        flash("Welcome back. Your secure session is active.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    log_activity("logout", {"email": g.current_user["email"]}, user_id=g.current_user["_id"])
    session.clear()
    flash("You have been signed out safely.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    inbox_count = mongo.db.messages.count_documents({"recipient_id": g.current_user["_id"]})
    sent_count = mongo.db.messages.count_documents({"sender_id": g.current_user["_id"]})
    file_count = mongo.db.secure_files.count_documents(
        {"$or": [{"sender_id": g.current_user["_id"]}, {"recipient_id": g.current_user["_id"]}]}
    )
    suspicious_count = (
        mongo.db.users.count_documents({"failed_login_count": {"$gte": 3}})
        if g.current_user["role"] == "Admin"
        else 0
    )
    recent_logs = list(
        mongo.db.activity_logs.find(
            {"user_id": g.current_user["_id"]},
            {"action": 1, "severity": 1, "created_at": 1},
        )
        .sort("created_at", -1)
        .limit(5)
    )

    dashboard_data = {
        "cards": [
            {"label": "Inbox", "value": inbox_count, "accent": "green"},
            {"label": "Sent Secure Emails", "value": sent_count, "accent": "blue"},
            {"label": "Shared Files", "value": file_count, "accent": "orange"},
            {"label": "Security Alerts", "value": suspicious_count, "accent": "red"},
        ]
    }
    return render_template(
        "dashboard.html",
        dashboard_data=dashboard_data,
        recent_logs=recent_logs,
    )


@app.route("/messages/compose", methods=["GET", "POST"])
@login_required
def compose_message():
    recipients = list(
        mongo.db.users.find(
            {"_id": {"$ne": g.current_user["_id"]}},
            {"full_name": 1, "email": 1, "role": 1},
        ).sort("full_name", 1)
    )

    if request.method == "POST":
        recipient_id = to_object_id(request.form.get("recipient_id"))
        subject = clean_text(request.form.get("subject"), 120)
        body = clean_text(request.form.get("body"), 5000)
        recipient = mongo.db.users.find_one({"_id": recipient_id})

        if not recipient:
            flash("Please choose a valid recipient.", "danger")
        elif len(subject) < 3:
            flash("Subject must be at least 3 characters long.", "danger")
        elif len(body) < 10:
            flash("Message body must be at least 10 characters long.", "danger")
        else:
            payload = {
                "subject": subject,
                "body": body,
                "message_type": "secure_email",
                "created_at": utc_now().isoformat(),
            }
            plaintext = json.dumps(payload, sort_keys=True).encode("utf-8")
            sender_private_key = get_user_private_key(g.current_user)
            envelope = encrypt_for_sender_and_recipient(
                plaintext,
                g.current_user["public_key_pem"],
                recipient["public_key_pem"],
            )
            message_document = {
                "sender_id": g.current_user["_id"],
                "recipient_id": recipient["_id"],
                "signature": sign_blob(sender_private_key, plaintext),
                "encrypted_payload": {
                    "nonce": envelope["nonce_b64"],
                    "ciphertext": envelope["ciphertext_b64"],
                    "encrypted_key_sender": envelope["encrypted_key_sender"],
                    "encrypted_key_recipient": envelope["encrypted_key_recipient"],
                },
                "message_type": "secure_email",
                "created_at": utc_now(),
            }
            inserted = mongo.db.messages.insert_one(message_document)
            log_activity(
                "message_sent",
                {"recipient": recipient["email"], "message_id": str(inserted.inserted_id)},
                user_id=g.current_user["_id"],
            )
            flash("Secure email sent. The body is stored encrypted with AES and RSA key wrapping.", "success")
            return redirect(url_for("message_detail", message_id=str(inserted.inserted_id)))

    return render_template("compose.html", recipients=recipients)


@app.route("/inbox")
@login_required
def inbox():
    user_lookup = build_user_lookup()
    messages = list(
        mongo.db.messages.find(
            {"$or": [{"sender_id": g.current_user["_id"]}, {"recipient_id": g.current_user["_id"]}]}
        )
        .sort("created_at", -1)
        .limit(25)
    )
    summaries = [message_to_view_model(message, g.current_user, user_lookup) for message in messages]
    inbox_data = {
        "received": sum(1 for item in summaries if item["direction"] == "Received"),
        "sent": sum(1 for item in summaries if item["direction"] == "Sent"),
        "valid_signatures": sum(1 for item in summaries if item["signature_valid"]),
    }
    return render_template("inbox.html", messages=summaries, inbox_data=inbox_data)


@app.route("/messages/<message_id>")
@login_required
def message_detail(message_id):
    message = mongo.db.messages.find_one({"_id": to_object_id(message_id)})
    if not message:
        abort(404)
    if not can_access_record(message, g.current_user["_id"]):
        abort(403)

    user_lookup = build_user_lookup()
    view_model = message_to_view_model(message, g.current_user, user_lookup)
    view_model["encrypted_preview"] = {
        "ciphertext": short_ciphertext(message["encrypted_payload"]["ciphertext"], 160),
        "encrypted_key_sender": short_ciphertext(
            message["encrypted_payload"]["encrypted_key_sender"], 120
        ),
        "encrypted_key_recipient": short_ciphertext(
            message["encrypted_payload"]["encrypted_key_recipient"], 120
        ),
        "signature": short_ciphertext(message["signature"], 120),
    }
    log_activity("message_opened", {"message_id": message_id}, user_id=g.current_user["_id"])
    return render_template("message_detail.html", message=view_model)


@app.route("/files")
@login_required
def files():
    user_lookup = build_user_lookup()
    file_records = list(
        mongo.db.secure_files.find(
            {"$or": [{"sender_id": g.current_user["_id"]}, {"recipient_id": g.current_user["_id"]}]}
        )
        .sort("created_at", -1)
        .limit(25)
    )
    files_view = [file_to_view_model(record, g.current_user, user_lookup) for record in file_records]
    return render_template("files.html", files=files_view)


@app.route("/files/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    recipients = list(
        mongo.db.users.find(
            {"_id": {"$ne": g.current_user["_id"]}},
            {"full_name": 1, "email": 1, "role": 1},
        ).sort("full_name", 1)
    )

    if request.method == "POST":
        recipient_id = to_object_id(request.form.get("recipient_id"))
        recipient = mongo.db.users.find_one({"_id": recipient_id})
        uploaded_file = request.files.get("secure_file")

        if not recipient:
            flash("Please choose a valid recipient.", "danger")
        elif not uploaded_file or uploaded_file.filename == "":
            flash("Please select a file to protect.", "danger")
        elif not allowed_file(uploaded_file.filename):
            flash("Only PDF and image files are allowed.", "danger")
        else:
            file_bytes = uploaded_file.read()
            original_filename = secure_filename(uploaded_file.filename)
            sender_private_key = get_user_private_key(g.current_user)
            envelope = encrypt_for_sender_and_recipient(
                file_bytes,
                g.current_user["public_key_pem"],
                recipient["public_key_pem"],
            )

            stored_filename = f"{uuid.uuid4().hex}.bin"
            storage_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)
            with open(storage_path, "wb") as encrypted_file:
                encrypted_file.write(envelope["ciphertext_bytes"])

            file_document = {
                "sender_id": g.current_user["_id"],
                "recipient_id": recipient["_id"],
                "original_filename": original_filename,
                "stored_filename": stored_filename,
                "mime_type": uploaded_file.mimetype or "application/octet-stream",
                "size": len(file_bytes),
                "sha256": sha256_hex(file_bytes),
                "signature": sign_blob(sender_private_key, file_bytes),
                "nonce": envelope["nonce_b64"],
                "encrypted_key_sender": envelope["encrypted_key_sender"],
                "encrypted_key_recipient": envelope["encrypted_key_recipient"],
                "ciphertext_preview": envelope["ciphertext_b64"][:160],
                "created_at": utc_now(),
            }
            inserted = mongo.db.secure_files.insert_one(file_document)
            log_activity(
                "file_uploaded",
                {"recipient": recipient["email"], "file_id": str(inserted.inserted_id)},
                user_id=g.current_user["_id"],
            )
            flash("File encrypted and stored successfully.", "success")
            return redirect(url_for("file_detail", file_id=str(inserted.inserted_id)))

    return render_template("upload_file.html", recipients=recipients)


@app.route("/files/<file_id>")
@login_required
def file_detail(file_id):
    file_record = mongo.db.secure_files.find_one({"_id": to_object_id(file_id)})
    if not file_record:
        abort(404)
    if not can_access_record(file_record, g.current_user["_id"]):
        abort(403)

    encrypted_key = (
        file_record["encrypted_key_sender"]
        if file_record["sender_id"] == g.current_user["_id"]
        else file_record["encrypted_key_recipient"]
    )
    private_key = get_user_private_key(g.current_user)
    storage_path = os.path.join(app.config["UPLOAD_FOLDER"], file_record["stored_filename"])

    with open(storage_path, "rb") as encrypted_file:
        encrypted_bytes = encrypted_file.read()

    decrypted_bytes = decrypt_for_viewer(
        nonce=base64.b64decode(file_record["nonce"]),
        ciphertext=encrypted_bytes,
        encrypted_key=encrypted_key,
        private_pem=private_key,
    )
    sender = mongo.db.users.find_one({"_id": file_record["sender_id"]}, {"public_key_pem": 1, "full_name": 1})
    signature_valid = verify_signature(sender["public_key_pem"], decrypted_bytes, file_record["signature"])
    user_lookup = build_user_lookup()
    view_model = file_to_view_model(file_record, g.current_user, user_lookup)
    view_model.update(
        {
            "signature_valid": signature_valid,
            "decrypted_sha256": sha256_hex(decrypted_bytes),
            "sender_name": sender["full_name"],
            "encrypted_key_sender": short_ciphertext(file_record["encrypted_key_sender"], 120),
            "encrypted_key_recipient": short_ciphertext(file_record["encrypted_key_recipient"], 120),
            "signature": short_ciphertext(file_record["signature"], 120),
        }
    )
    log_activity("file_metadata_opened", {"file_id": file_id}, user_id=g.current_user["_id"])
    return render_template("file_detail.html", secure_file=view_model)


@app.route("/files/<file_id>/download")
@login_required
def download_file(file_id):
    file_record = mongo.db.secure_files.find_one({"_id": to_object_id(file_id)})
    if not file_record:
        abort(404)
    if not can_access_record(file_record, g.current_user["_id"]):
        abort(403)

    encrypted_key = (
        file_record["encrypted_key_sender"]
        if file_record["sender_id"] == g.current_user["_id"]
        else file_record["encrypted_key_recipient"]
    )
    private_key = get_user_private_key(g.current_user)
    storage_path = os.path.join(app.config["UPLOAD_FOLDER"], file_record["stored_filename"])

    with open(storage_path, "rb") as encrypted_file:
        encrypted_bytes = encrypted_file.read()

    decrypted_bytes = decrypt_for_viewer(
        nonce=base64.b64decode(file_record["nonce"]),
        ciphertext=encrypted_bytes,
        encrypted_key=encrypted_key,
        private_pem=private_key,
    )
    log_activity("file_downloaded", {"file_id": file_id}, user_id=g.current_user["_id"])
    return send_file(
        BytesIO(decrypted_bytes),
        as_attachment=True,
        download_name=file_record["original_filename"],
        mimetype=file_record["mime_type"],
    )


@app.route("/security-concepts")
@login_required
def security_concepts():
    return render_template(
        "security_concepts.html",
        concepts=SECURITY_CONCEPTS,
        access_control_matrix=ACCESS_CONTROL_MATRIX,
    )


@app.route("/admin")
@role_required("Admin")
def admin_panel():
    users = list(
        mongo.db.users.find(
            {},
            {
                "full_name": 1,
                "email": 1,
                "role": 1,
                "failed_login_count": 1,
                "created_at": 1,
                "last_failed_login": 1,
            },
        ).sort("created_at", -1)
    )
    suspicious_users = [user for user in users if user.get("failed_login_count", 0) >= 3]
    logs = list(
        mongo.db.activity_logs.find({}, {"action": 1, "details": 1, "severity": 1, "created_at": 1})
        .sort("created_at", -1)
        .limit(30)
    )
    return render_template("admin.html", users=users, suspicious_users=suspicious_users, logs=logs)


@app.route("/admin/seed-demo", methods=["POST"])
@role_required("Admin")
def admin_seed_demo():
    summary = seed_demo_data(
        mongo.db,
        app.config["PRIVATE_KEY_WRAP_SECRET"],
        app.config["UPLOAD_FOLDER"],
    )
    log_activity("demo_seeded", summary, user_id=g.current_user["_id"])
    flash(
        "Demo data is ready: admin@ngo.local / Admin@123 and staff@ngo.local / Staff@123.",
        "success",
    )
    return redirect(url_for("admin_panel"))


@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="You do not have access to this resource."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="The requested page could not be found."), 404


@app.errorhandler(413)
def file_too_large(_error):
    flash("The uploaded file is too large. Keep demo files under 10 MB.", "danger")
    return redirect(url_for("upload_file"))


def parse_args():
    parser = argparse.ArgumentParser(description="Secure Communication Platform for Non-Profit Organizations")
    parser.add_argument(
        "--seed-demo",
        action="store_true",
        help="Create demo users, a sample secure email, and a sample encrypted file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.seed_demo:
        with app.app_context():
            summary = seed_demo_data(
                mongo.db,
                app.config["PRIVATE_KEY_WRAP_SECRET"],
                app.config["UPLOAD_FOLDER"],
            )
            print("Demo data ready:", summary)
    app.run(debug=True)
