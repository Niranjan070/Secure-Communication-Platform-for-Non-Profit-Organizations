# Secure Communication Platform for Non-Profit Organizations

## Table of Contents

1. [Project Overview](#project-overview)
2. [Abstract](#abstract)
3. [Problem Statement](#problem-statement)
4. [Objectives](#objectives)
5. [Project Scope](#project-scope)
6. [Key Features](#key-features)
7. [Technology Stack](#technology-stack)
8. [System Architecture](#system-architecture)
9. [Project Structure](#project-structure)
10. [Functional Workflow](#functional-workflow)
11. [Security Design](#security-design)
12. [Database Design](#database-design)
13. [Access Control Model](#access-control-model)
14. [Installation and Execution](#installation-and-execution)
15. [Environment Variables](#environment-variables)
16. [Demo Accounts](#demo-accounts)
17. [Suggested Demonstration Flow](#suggested-demonstration-flow)
18. [Implementation Status](#implementation-status)
19. [Limitations](#limitations)
20. [Future Enhancements](#future-enhancements)
21. [Conclusion](#conclusion)

## Project Overview

This project is a secure internal communication platform designed for non-profit and NGO teams. It demonstrates how core cybersecurity concepts can be implemented in a practical web application instead of being discussed only in theory.

The platform allows registered users to:

- create accounts and log in securely
- send encrypted internal messages
- upload and exchange encrypted files
- verify message and file authenticity using digital signatures
- enforce role-based access control
- monitor security-related events through an admin dashboard

The application is intended as an academic or demonstration project. It is strong as a learning prototype and presentation-ready system, but it is not positioned as a fully hardened production deployment.

## Abstract

Non-profit organizations often handle sensitive donor information, internal reports, beneficiary details, and operational files. These organizations may not always have access to enterprise-grade secure communication tools, which increases the risk of data leakage, tampering, and unauthorized access.

This project addresses that problem by building a web-based secure communication platform using Flask, MongoDB, and modern cryptographic techniques. The system applies bcrypt password hashing for authentication security, AES-256-GCM for payload encryption, RSA-2048 for key protection, and RSA-PSS digital signatures for integrity verification. In addition, the application includes CSRF protection, access control, session security, audit logging, and suspicious login monitoring.

The project bridges cybersecurity theory and implementation by showing how confidentiality, integrity, authentication, authorization, and accountability can be enforced in a real workflow for secure messaging and file sharing.

## Problem Statement

NGOs and non-profit organizations frequently work with confidential operational data, volunteer records, donor details, and internal planning documents. If such data is transmitted or stored insecurely, it becomes vulnerable to:

- unauthorized access
- insider misuse
- accidental data exposure
- tampering during storage or transfer
- weak authentication practices

The goal of this project is to provide a secure internal communication system that reduces these risks while also serving as a practical demonstration of applied information security concepts.

## Objectives

The main objectives of this project are:

- to build a secure communication platform for internal organizational use
- to protect sensitive messages and files using encryption
- to verify authenticity and integrity using digital signatures
- to enforce role-based access control between admin and staff users
- to record activity for auditing and monitoring purposes
- to map academic cybersecurity concepts to a functioning software system

## Project Scope

This project covers the following scope:

- web-based user registration and login
- internal secure messaging between registered users
- encrypted file upload, storage, inspection, and download
- admin oversight for users and activity logs
- educational presentation of cybersecurity concepts through a dedicated theory page

The project does not include:

- deployment automation
- production-grade infrastructure hardening
- client-side end-to-end cryptography with private keys held only by the user
- automated unit or integration tests

## Key Features

### 1. Authentication and Account Security

- password hashing using bcrypt
- email normalization and validation
- password policy enforcement
- failed login count tracking
- suspicious login alerting after repeated failures
- session-based authentication with secure cookie settings

### 2. Role-Based Access Control

- two user roles: `Admin` and `Staff`
- admins can access administrative views and monitoring tools
- staff users can access their own communication and shared files
- encrypted content is restricted to the sender and recipient

### 3. Encrypted Messaging

- secure internal message composition
- AES-256-GCM encryption for message content
- RSA-2048 encryption of the AES key for both sender and recipient
- RSA-PSS digital signatures for message verification
- encrypted message storage in MongoDB

### 4. Secure File Sharing

- PDF and image uploads
- file encryption before storage
- encrypted files saved on disk as `.bin` blobs
- SHA-256 checksum generation for integrity checking
- digital signature verification for uploaded files

### 5. Web Security Controls

- CSRF protection for state-changing forms
- input cleaning and server-side validation
- upload size limit of 10 MB
- file type whitelisting
- HTTPOnly and SameSite session cookies
- optional HTTPS-only cookie enforcement through environment configuration

### 6. Admin Monitoring

- registered user listing
- suspicious login activity visibility
- recent activity log review
- demo data seeding for presentations and evaluation

### 7. Theory Integration

- dedicated security concepts page
- mapping of application features to academic cybersecurity modules
- access control matrix for role permissions

## Technology Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Backend | Python 3.11+, Flask 3.x | Application logic and routing |
| Frontend | Jinja2 templates, HTML, CSS, JavaScript | User interface |
| UI Enhancements | Lightweight React via CDN | Dashboard and concept cards |
| Database | MongoDB with PyMongo | Users, messages, file metadata, logs |
| Cryptography | `cryptography` library | AES, RSA, signatures, checksums |
| Password Security | `bcrypt` | Password hashing |
| Form Security | Flask-WTF | CSRF protection |
| Configuration | `python-dotenv` | Environment variable loading |

## System Architecture

The application follows a simple layered architecture:

```text
+-----------------------------+
|        Client Browser       |
|   HTML / CSS / JS / Jinja   |
+-------------+---------------+
              |
              | HTTP / HTTPS
              v
+-----------------------------+
|       Flask Application     |
|  Routes, sessions, access   |
|  control, validation, UI    |
+-------------+---------------+
              |
              +------------------------------+
              |                              |
              v                              v
+-----------------------------+   +-----------------------------+
|     Crypto Utility Layer    |   |        MongoDB Layer        |
| AES-GCM, RSA-OAEP, RSA-PSS  |   | users, messages, files,     |
| key wrapping, signatures    |   | activity logs               |
+-------------+---------------+   +-----------------------------+
              |
              v
+-----------------------------+
|   Encrypted File Storage    |
|      uploads/*.bin          |
+-----------------------------+
```

### Architectural Summary

- the browser interacts with Flask through web pages and forms
- Flask handles business logic, authentication, validation, and authorization
- cryptographic operations are delegated to utility functions
- MongoDB stores structured records such as users, messages, metadata, and logs
- encrypted file bytes are stored separately on disk in the `uploads/` directory

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
|   |-- base.html
|   |-- login.html
|   |-- register.html
|   |-- dashboard.html
|   |-- compose.html
|   |-- inbox.html
|   |-- message_detail.html
|   |-- files.html
|   |-- upload_file.html
|   |-- file_detail.html
|   |-- admin.html
|   |-- security_concepts.html
|   `-- error.html
|-- static/
|   |-- css/
|   |   `-- style.css
|   `-- js/
|       |-- main.js
|       `-- react-app.js
|-- sample_data/
|   `-- demo-policy.pdf
`-- uploads/
```

### Important Files

- `app.py`: main Flask application, routes, authentication flow, and feature logic
- `database/db.py`: MongoDB connection and index creation
- `utils/crypto_utils.py`: encryption, decryption, key generation, signatures, hashing
- `utils/demo_data.py`: reusable demo data generation
- `utils/security_helpers.py`: validation and helper functions
- `utils/theory_content.py`: security theory content and access control matrix

## Functional Workflow

### 1. User Registration

When a new user registers:

1. the system validates the name, email, and password
2. the password is hashed using bcrypt
3. an RSA-2048 public/private key pair is generated
4. the private key is wrapped using AES-GCM with a server-side secret
5. the user record is stored in MongoDB

This ensures that passwords are not stored in plain text and that each user has a cryptographic identity for secure communication.

### 2. User Login

When a user logs in:

1. the email is normalized and matched against the database
2. the password is verified using bcrypt
3. failed login attempts are counted
4. suspicious behavior is flagged after repeated failures
5. a Flask session is created for authenticated access
6. the activity is recorded in the audit log

### 3. Secure Message Sending

When a user sends a secure message:

1. the sender writes the subject and body
2. the system creates a plaintext JSON payload
3. a random AES-256 key is generated
4. the message payload is encrypted using AES-256-GCM
5. the AES key is encrypted with the sender's RSA public key
6. the AES key is encrypted again with the recipient's RSA public key
7. the sender signs the plaintext using RSA-PSS
8. the encrypted payload, wrapped keys, and signature are stored in MongoDB

As a result, the stored message body remains encrypted at rest.

### 4. Secure Message Reading

When a sender or recipient opens a message:

1. the system checks whether that user is authorized to view the record
2. the correct RSA-wrapped AES key is selected
3. the user's wrapped private key is unwrapped on the server
4. the AES key is decrypted using RSA
5. the original message content is recovered using AES-GCM
6. the sender's public key is used to verify the digital signature

### 5. Secure File Upload

When a file is uploaded:

1. the file type is validated against an allowed extension list
2. the file is read into memory
3. a SHA-256 checksum is computed from the original file bytes
4. the file bytes are encrypted using AES-256-GCM
5. the AES key is wrapped separately for the sender and recipient
6. the original file is signed using the sender's private key
7. the encrypted bytes are stored on disk as a `.bin` file
8. file metadata is stored in MongoDB

### 6. Secure File Inspection and Download

When an authorized user inspects or downloads a file:

1. access control verifies that the user is the sender or recipient
2. the encrypted file bytes are loaded from storage
3. the appropriate RSA-wrapped AES key is decrypted
4. the file bytes are recovered using AES-GCM
5. the signature is verified
6. the checksum can be compared to confirm integrity
7. the file can be downloaded in its original format

### 7. Admin Monitoring

Admin users can:

- view registered users
- identify accounts with repeated failed logins
- review recent activity logs
- seed demo data for presentation and testing

## Security Design

This project demonstrates multiple security properties together rather than focusing on encryption alone.

| Security Goal | Mechanism Used | Implementation |
| --- | --- | --- |
| Confidentiality | AES-256-GCM | protects message and file payloads |
| Secure key exchange | RSA-2048 OAEP | protects the AES key for sender and recipient |
| Integrity | AES-GCM authentication and SHA-256 | ensures data is not silently altered |
| Authentication | bcrypt and session-based login | secures user access |
| Digital verification | RSA-PSS signatures | verifies sender and detects tampering |
| Authorization | role checks and sender/recipient checks | restricts sensitive operations |
| CSRF protection | Flask-WTF | protects form submissions |
| Session security | HTTPOnly, SameSite, optional Secure cookies | strengthens web session handling |
| Auditability | activity logs | tracks key actions across the platform |

### Why Hybrid Encryption Is Used

RSA is not efficient for encrypting large amounts of data such as message bodies or files. AES is much faster for bulk encryption. Therefore, the application uses a hybrid model:

- AES encrypts the actual content
- RSA encrypts the AES key
- digital signatures verify who sent the content and whether it was changed

This is the same core idea behind practical secure communication systems such as PGP-style workflows.

### Cryptographic Flow

```text
Sender
  |
  |-- Generate random AES-256 key
  |-- Encrypt message or file with AES-GCM
  |-- Encrypt AES key with sender public RSA key
  |-- Encrypt AES key with recipient public RSA key
  |-- Sign original plaintext with sender private RSA key
  |
  +---- Store ciphertext + wrapped keys + signature ----> Database / Encrypted storage

Recipient or Sender
  |
  |-- Select the correct wrapped AES key
  |-- Decrypt AES key using private RSA key
  |-- Decrypt payload using AES-GCM
  |-- Verify signature using sender public RSA key
  |
  +---- View trusted plaintext
```

## Database Design

The application uses MongoDB with the following main collections:

### 1. `users`

Stores:

- full name
- email address
- password hash
- role
- public RSA key
- wrapped private RSA key
- failed login count
- timestamps

### 2. `messages`

Stores:

- sender ID
- recipient ID
- encrypted payload
- wrapped AES keys for sender and recipient
- digital signature
- message type
- creation time

### 3. `secure_files`

Stores:

- sender ID
- recipient ID
- original filename
- stored encrypted filename
- MIME type
- file size
- SHA-256 hash
- wrapped AES keys
- digital signature
- nonce
- ciphertext preview
- creation time

### 4. `activity_logs`

Stores:

- user ID
- action name
- details
- severity
- timestamp

### Database Indexing

Indexes are created for:

- unique email lookup
- role lookup
- inbox and sent-item retrieval
- secure file retrieval
- activity log sorting and filtering

These indexes improve performance for common operations such as login, inbox viewing, and activity monitoring.

## Access Control Model

The system uses role-based access control together with ownership-based restrictions.

| Resource | Admin | Staff |
| --- | --- | --- |
| Dashboard | Yes | Yes |
| Own inbox and sent messages | Yes | Yes |
| Own shared files | Yes | Yes |
| Compose message | Yes | Yes |
| Upload file | Yes | Yes |
| Security concepts page | Yes | Yes |
| Admin panel | Yes | No |
| Seed demo data | Yes | No |
| View other users' encrypted content | No | No |

### Access Control Rules

- only authenticated users can access application features
- only admins can open the admin panel
- only the sender or recipient can inspect or decrypt a message
- only the sender or recipient can inspect or download a protected file

## Installation and Execution

### Prerequisites

- Python 3.11 or later
- MongoDB running locally on port `27017`

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "Data and information security"
```

### 2. Create a Virtual Environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start MongoDB

Ensure MongoDB is running locally and accessible at:

```text
mongodb://127.0.0.1:27017/secure_ngo_platform
```

### 5. Seed Demo Data

```bash
python app.py --seed-demo
```

This creates:

- one admin user
- one staff user
- one encrypted demo message
- one encrypted demo PDF file

### 6. Run the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## Environment Variables

The application supports the following configuration values:

| Variable | Default Value | Description |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | `change-this-flask-secret` | secret used for Flask sessions |
| `PRIVATE_KEY_WRAP_SECRET` | `change-this-private-key-wrap-secret` | secret used to wrap stored private keys |
| `MONGO_URI` | `mongodb://127.0.0.1:27017/secure_ngo_platform` | MongoDB connection string |
| `ENABLE_HTTPS_ONLY` | `false` | when `true`, session cookies are marked Secure |

### Example `.env`

```env
FLASK_SECRET_KEY=replace-with-a-strong-random-secret
PRIVATE_KEY_WRAP_SECRET=replace-with-another-strong-random-secret
MONGO_URI=mongodb://127.0.0.1:27017/secure_ngo_platform
ENABLE_HTTPS_ONLY=false
```

For any real deployment, these secrets must be changed to strong unique values.

## Demo Accounts

After seeding demo data, the following accounts are available:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@ngo.local` | `Admin@123` |
| Staff | `staff@ngo.local` | `Staff@123` |

## Suggested Demonstration Flow

This order works well for a project demo, report screenshots, or viva presentation:

1. log in as the admin account
2. show the dashboard and explain the security summary cards
3. open the admin panel and discuss user management, audit logs, and suspicious login monitoring
4. open the inbox and view a secure message
5. point out that the decrypted content is shown to the user, while encrypted payload details are stored separately
6. open the files section and inspect the demo PDF
7. show the checksum, signature status, and decrypt-and-download flow
8. visit the security concepts page to connect the implementation with academic theory

## Implementation Status

The current repository is functionally complete for academic demonstration and report generation.

### Implemented

- user registration
- user login and logout
- bcrypt password hashing
- per-user RSA key generation
- wrapped private key storage
- encrypted messaging
- encrypted file storage and retrieval
- digital signature verification
- role-based access control
- CSRF protection
- audit logging
- suspicious login monitoring
- demo data seeding
- theory mapping page

### Not Included

- automated tests
- production deployment configuration
- Docker setup
- client-side end-to-end key management
- email or notification integration with external services

## Limitations

This section is important for transparency in a report or viva.

1. The system is an academic prototype, not a production-hardened platform.
2. Private keys are stored on the server in wrapped form. This means the application demonstrates strong secure storage and controlled decryption, but not pure end-to-end encryption where only the user device holds the private key.
3. The development server runs with debug mode enabled in the current codebase.
4. There are no automated unit tests or integration tests.
5. HTTPS is recommended for production, but certificate management and deployment setup are outside the scope of this repository.
6. The lightweight React widgets are loaded from a CDN, so those UI enhancements depend on internet access.

## Future Enhancements

The following improvements can strengthen the project further:

- move private key custody to the client side for stronger end-to-end guarantees
- add rate limiting and account lockout
- add automated unit and integration tests
- containerize the application with Docker
- add production deployment configuration
- support more file types with malware scanning
- add notification services and stronger monitoring
- improve key rotation and recovery policies

## Conclusion

This project successfully demonstrates how core data and information security concepts can be applied in a practical software system. It combines authentication, encryption, digital signatures, access control, web security, and audit logging into a single coherent application for secure NGO communication.

As an academic project, it provides a strong example of secure system design with real implementation value. It is especially suitable for coursework, project reports, demonstrations, and panel presentations because it clearly connects cybersecurity theory to working software behavior.
