# Secure Communication Platform for Non-Profit Organizations

This project is a Flask + MongoDB web application that demonstrates secure communication for NGO teams. It includes:

- User registration and login with `bcrypt` password hashing
- Role-based access for `Admin` and `Staff`
- Encrypted internal email using AES + RSA key wrapping
- Secure file sharing with encrypted storage and digital signatures
- RSA-based digital signature verification for messages and files
- CSRF protection, secure Flask session settings, and activity logging
- A dedicated **Security Concepts** page mapping the implementation to cybersecurity theory

## Tech Stack

- Backend: Flask, Python
- Frontend: Server-rendered HTML + CSS + JavaScript with React dashboard widgets
- Database: MongoDB
- Security libraries: `cryptography`, `bcrypt`, `Flask-WTF`

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
|-- database/
|   `-- db.py
|-- utils/
|   |-- crypto_utils.py
|   |-- demo_data.py
|   |-- security_helpers.py
|   `-- theory_content.py
|-- templates/
|   |-- admin.html
|   |-- base.html
|   |-- compose.html
|   |-- dashboard.html
|   |-- error.html
|   |-- file_detail.html
|   |-- files.html
|   |-- inbox.html
|   |-- login.html
|   |-- message_detail.html
|   |-- register.html
|   |-- security_concepts.html
|   `-- upload_file.html
|-- static/
|   |-- css/
|   |   `-- style.css
|   `-- js/
|       |-- main.js
|       `-- react-app.js
|-- uploads/
`-- sample_data/
    `-- demo-policy.pdf
```

## Setup Instructions

1. Install Python 3.11+ and MongoDB Community Server.
2. Start MongoDB locally so the app can connect to `mongodb://127.0.0.1:27017/secure_ngo_platform`.
3. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Optional: set environment variables in PowerShell before running:

   ```powershell
   $env:FLASK_SECRET_KEY="replace-with-a-long-random-secret"
   $env:PRIVATE_KEY_WRAP_SECRET="replace-with-another-long-random-secret"
   $env:MONGO_URI="mongodb://127.0.0.1:27017/secure_ngo_platform"
   $env:ENABLE_HTTPS_ONLY="false"
   ```

6. Seed the demo users, encrypted message, and encrypted file:

   ```powershell
   python app.py --seed-demo
   ```

7. Run the application:

   ```powershell
   python app.py
   ```

8. Open the app in your browser:

   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Demo Accounts

- Admin: `admin@ngo.local` / `Admin@123`
- Staff: `staff@ngo.local` / `Staff@123`

## Demo Workflow

1. Log in as `admin@ngo.local`.
2. Open the **Admin** page and confirm the seeded users exist.
3. Visit **Inbox** and open the seeded encrypted message.
4. Notice the page shows:
   - Decrypted subject and body
   - AES ciphertext preview
   - RSA-wrapped AES keys
   - Digital signature status
5. Open **Files** and inspect the seeded `demo-policy.pdf`.
6. Download the file to confirm it is decrypted only at access time.
7. Send a new secure email or upload a new file to test the full workflow.

## Security Features Mapped to Theory

- Module 2: Threats, policies, access control matrix, admin monitoring
- Module 3: AES symmetric encryption, RSA asymmetric key exchange, encrypted storage
- Module 4: RSA digital signatures for integrity and authentication
- Module 5: PGP-style secure internal email and IP security explanations
- Module 6: Web security with CSRF protection, secure sessions, HTTPS guidance, validation

## Notes for Local HTTPS

For a classroom demo, HTTP is acceptable locally. In production, place the Flask app behind an HTTPS-enabled reverse proxy or run Flask with a certificate. The `SESSION_COOKIE_SECURE` setting can be enabled with:

```powershell
$env:ENABLE_HTTPS_ONLY="true"
```

## Sample Test Data

- Seeded users: admin + staff
- Seeded secure email: `Shelter inventory update`
- Seeded secure file: `sample_data/demo-policy.pdf`

## Important Implementation Notes

- Passwords are hashed with `bcrypt` and never stored in plaintext.
- Messages and file contents are encrypted with AES-GCM before storage.
- AES keys are wrapped with RSA for both sender and recipient.
- Digital signatures are created with the sender's RSA private key and verified with the public key.
- Flask-WTF CSRF protection is enabled for all state-changing form submissions.
- Audit logs record login attempts, message access, uploads, downloads, and demo seeding actions.
