# 🔐 Secure Communication Platform for Non-Profit Organizations

A full-stack web application demonstrating **end-to-end secure communication** for NGO teams. The platform implements real-world cryptographic protocols — AES-256-GCM encryption, RSA-2048 key exchange, and digital signatures — within a practical messaging and file-sharing workflow.

Built as an academic project to bridge the gap between **cybersecurity theory and hands-on implementation**.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.x+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Demo Walkthrough](#-demo-walkthrough)
- [Security Implementation](#-security-implementation)
- [Cryptographic Flow](#-cryptographic-flow)
- [Security Concepts Mapped to Theory](#-security-concepts-mapped-to-theory)
- [Environment Variables](#-environment-variables)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)

---

## ✨ Features

### 🔑 Authentication & Access Control
- **Bcrypt password hashing** — passwords are never stored in plaintext
- **Role-based access control** — `Admin` and `Staff` roles with distinct privileges
- **Failed login tracking** — brute-force detection with audit alerts after 3+ failed attempts
- **Secure session management** — HTTPOnly cookies, SameSite policy, configurable HTTPS-only mode

### 📧 Encrypted Internal Email
- **AES-256-GCM symmetric encryption** for message content
- **RSA-2048 key wrapping** — AES key encrypted for both sender and recipient
- **RSA-PSS digital signatures** for integrity verification and non-repudiation
- Messages are stored fully encrypted; decryption happens only at access time

### 📁 Secure File Sharing
- Upload PDFs and images with automatic **client-to-storage encryption**
- Files stored as `.bin` blobs — unreadable without proper RSA key decryption
- **SHA-256 checksums** for file integrity verification
- Digital signature verification on every download

### 🛡️ Web Security
- **CSRF protection** on all state-changing forms via Flask-WTF
- Input validation and sanitization on all user inputs
- 10 MB upload limit with file type whitelisting (PDF, PNG, JPG, JPEG)
- Secure cookie configuration with configurable HTTPS enforcement

### 📊 Admin Dashboard
- View all registered users and their roles
- Monitor **security alerts** — accounts with suspicious login patterns
- Full **audit log** of platform activity (logins, messages, uploads, downloads)
- Seed demo data for classroom demonstrations

### 📚 Security Concepts Page
- Interactive reference mapping every feature to **cybersecurity theory modules**
- Access Control Matrix visualization
- Covers: threat modeling, symmetric/asymmetric encryption, digital signatures, PGP-style email, and web security

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Client Browser                    │
│         HTML/CSS/JS  +  React Dashboard Widgets      │
└──────────────────────┬──────────────────────────────┘
                       │  HTTPS (recommended) / HTTP
┌──────────────────────▼──────────────────────────────┐
│                 Flask Application                    │
│  ┌──────────┐  ┌───────────┐  ┌───────────────────┐ │
│  │  Routes  │  │   Auth    │  │  CSRF Protection  │ │
│  │ & Views  │  │ Middleware│  │   (Flask-WTF)     │ │
│  └────┬─────┘  └─────┬─────┘  └───────────────────┘ │
│       │              │                               │
│  ┌────▼──────────────▼──────────────────────────┐   │
│  │            Crypto Engine                      │   │
│  │  AES-256-GCM  |  RSA-2048 OAEP  |  RSA-PSS  │   │
│  │  Key Wrapping  |  Digital Signatures          │   │
│  └────────────────────┬─────────────────────────┘   │
└───────────────────────┼─────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼                               ▼
┌───────────────┐              ┌──────────────────┐
│   MongoDB     │              │  Encrypted File  │
│  ─ users      │              │    Storage       │
│  ─ messages   │              │  (uploads/*.bin) │
│  ─ files      │              └──────────────────┘
│  ─ audit_logs │
└───────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, Flask 3.x |
| **Frontend** | Server-rendered Jinja2 templates, CSS, JavaScript, React widgets |
| **Database** | MongoDB with PyMongo |
| **Cryptography** | `cryptography` library (AES-GCM, RSA-OAEP, RSA-PSS) |
| **Authentication** | `bcrypt` for password hashing |
| **Security** | Flask-WTF (CSRF), secure session cookies |
| **Config** | `python-dotenv` for environment variables |

---

## 📂 Project Structure

```
.
├── app.py                    # Main Flask application (routes, middleware, logic)
├── requirements.txt          # Python dependencies
├── README.md
├── .gitignore
│
├── database/
│   └── db.py                 # MongoDB connection + index initialization
│
├── utils/
│   ├── crypto_utils.py       # AES-GCM, RSA-OAEP, RSA-PSS, key wrapping
│   ├── demo_data.py          # Seed script for demo users, messages, files
│   ├── security_helpers.py   # Input validation, email normalization, utilities
│   └── theory_content.py     # Security concepts & access control matrix data
│
├── templates/
│   ├── base.html             # Base layout with navigation
│   ├── login.html            # Login page
│   ├── register.html         # User registration
│   ├── dashboard.html        # Main dashboard with stats
│   ├── compose.html          # Compose encrypted email
│   ├── inbox.html            # Message inbox
│   ├── message_detail.html   # Decrypted message view with crypto details
│   ├── files.html            # Secure file listing
│   ├── upload_file.html      # Upload & encrypt file
│   ├── file_detail.html      # File details with signature verification
│   ├── admin.html            # Admin panel (users, logs, alerts)
│   ├── security_concepts.html# Theory-to-implementation mapping
│   └── error.html            # Error pages (403, 404)
│
├── static/
│   ├── css/
│   │   └── style.css         # Application styles
│   └── js/
│       ├── main.js           # Core JavaScript
│       └── react-app.js      # React dashboard components
│
├── uploads/                  # Encrypted file storage (*.bin)
└── sample_data/
    └── demo-policy.pdf       # Sample file for demo seeding
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **MongoDB Community Server** — [Download](https://www.mongodb.com/try/download/community)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Niranjan070/Secure-Communication-Platform-for-Non-Profit-Organizations.git
   cd Secure-Communication-Platform-for-Non-Profit-Organizations
   ```

2. **Start MongoDB** — ensure it is running locally on the default port (`27017`)

3. **Create a virtual environment**

   ```powershell
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   ```bash
   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Seed demo data** (creates demo users, an encrypted message, and an encrypted file)

   ```bash
   python app.py --seed-demo
   ```

6. **Open in your browser**

   ```
   http://127.0.0.1:5000
   ```

---

## 🎮 Demo Walkthrough

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@ngo.local` | `Admin@123` |
| **Staff** | `staff@ngo.local` | `Staff@123` |

### Try This

1. **Log in** as `admin@ngo.local` → explore the **Dashboard** with stats cards
2. Open the **Admin** panel → view registered users and audit logs
3. Visit **Inbox** → open the seeded encrypted message and observe:
   - Decrypted subject and body
   - AES ciphertext preview (proving data is encrypted at rest)
   - RSA-wrapped AES keys for both sender and recipient
   - Digital signature verification status ✅
4. Open **Files** → inspect the seeded `demo-policy.pdf`
5. **Download** the file to verify it decrypts correctly on access
6. **Compose** a new secure email or **upload** a new file to test the full end-to-end workflow
7. Visit **Security Concepts** to see the theory-to-implementation mapping

---

## 🔒 Security Implementation

### Password Storage
Passwords are hashed using **bcrypt** with an auto-generated salt. The raw password is never stored or logged.

### Per-User RSA Key Pairs
On registration, each user receives a unique **RSA-2048 key pair**:
- **Public key** — stored in plaintext for encrypting messages addressed to the user
- **Private key** — wrapped (encrypted) with AES-256-GCM using a server-side secret before storage

### Message Encryption (Hybrid Cryptosystem)
Messages use a **PGP-style hybrid encryption** approach:
1. A random **AES-256 key** is generated per message
2. The message body is encrypted with **AES-256-GCM** (authenticated encryption)
3. The AES key is wrapped with the **sender's RSA public key** (so the sender can decrypt their own sent messages)
4. The AES key is also wrapped with the **recipient's RSA public key**
5. A **RSA-PSS digital signature** is created with the sender's private key

### File Encryption
Files follow the same hybrid pattern:
- File bytes are encrypted with AES-256-GCM
- The encrypted blob is stored as a `.bin` file on disk
- Decryption only occurs when an authorized user accesses the file
- SHA-256 hash is computed pre-encryption for integrity verification

---

## 🔄 Cryptographic Flow

```
Sender                                              Recipient
  │                                                      │
  │  1. Generate random AES-256 key                      │
  │  2. Encrypt plaintext with AES-256-GCM               │
  │  3. Wrap AES key with Sender's RSA public key        │
  │  4. Wrap AES key with Recipient's RSA public key     │
  │  5. Sign plaintext with Sender's RSA private key     │
  │                                                      │
  │  ─── Store in MongoDB (all encrypted) ──────────►    │
  │                                                      │
  │                    6. Unwrap AES key with             │
  │                       Recipient's RSA private key     │
  │                    7. Decrypt with AES-256-GCM        │
  │                    8. Verify signature with           │
  │                       Sender's RSA public key         │
  │                                                      │
```

---

## 📖 Security Concepts Mapped to Theory

| Module | Topic | Implementation |
|--------|-------|---------------|
| **Module 2** | Threats & Access Control | Role-based access (Admin/Staff), access control matrix, brute-force detection, audit logging |
| **Module 3** | Symmetric & Asymmetric Encryption | AES-256-GCM for data, RSA-2048 OAEP for key exchange, hybrid encryption model |
| **Module 4** | Digital Signatures | RSA-PSS signatures for message integrity, authentication, and non-repudiation |
| **Module 5** | PGP & IP Security | PGP-style hybrid email encryption, key pair lifecycle, secure internal messaging |
| **Module 6** | Web Security | CSRF tokens (Flask-WTF), secure sessions (HTTPOnly, SameSite), input validation, HTTPS guidance |

---

## ⚙️ Environment Variables

Configure these in a `.env` file or set them in your shell before running:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_SECRET_KEY` | `change-this-flask-secret` | Secret key for Flask sessions |
| `PRIVATE_KEY_WRAP_SECRET` | `change-this-private-key-wrap-secret` | Secret for wrapping RSA private keys |
| `MONGO_URI` | `mongodb://127.0.0.1:27017/secure_ngo_platform` | MongoDB connection string |
| `ENABLE_HTTPS_ONLY` | `false` | Set to `true` to enforce secure cookies |

> ⚠️ **For production use**, always set strong, unique values for `FLASK_SECRET_KEY` and `PRIVATE_KEY_WRAP_SECRET`.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with 🔒 by <a href="https://github.com/Niranjan070">Niranjan</a>
</p>
