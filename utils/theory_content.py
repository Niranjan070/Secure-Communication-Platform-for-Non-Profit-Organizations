SECURITY_CONCEPTS = [
    {
        "id": "module-2",
        "title": "Module 2: Security Investigations",
        "summary": "NGOs handle donor information, field reports, and beneficiary data that are attractive to both criminals and insiders.",
        "points": [
            "Threats include phishing, device theft, insider misuse, ransomware, and accidental leaks during volunteer handoffs.",
            "Confidentiality keeps case files and donor identities private, while integrity protects report accuracy and audit trails.",
            "An access control matrix helps map who can read, write, verify, or administer each resource in the platform.",
            "Security policies should define onboarding, password rules, incident reporting, and least-privilege access.",
        ],
    },
    {
        "id": "module-3",
        "title": "Module 3: Encryption",
        "summary": "This project combines symmetric and asymmetric cryptography to protect messages and files.",
        "points": [
            "AES is used for fast symmetric encryption of message bodies and uploaded file content before storage.",
            "RSA is used to wrap the AES key for the sender and recipient so only authorized users can decrypt it.",
            "Diffie-Hellman is not implemented here, but it is commonly used to agree on a shared secret across an insecure network.",
            "The database stores ciphertext, not the original NGO communication payloads.",
        ],
    },
    {
        "id": "module-4",
        "title": "Module 4: Digital Signature",
        "summary": "Digital signatures provide integrity and sender authentication.",
        "points": [
            "The sender signs the plaintext message or file bytes with their RSA private key before sharing it.",
            "The receiver verifies the signature with the sender's public key to confirm the content has not been altered.",
            "A failed verification indicates tampering, corruption, or a mismatched key pair.",
        ],
    },
    {
        "id": "module-5",
        "title": "Module 5: Email and IP Security",
        "summary": "The internal email module mirrors PGP-style messaging by combining encryption and signatures.",
        "points": [
            "PGP and S/MIME both combine confidentiality with message authentication for email communication.",
            "This app simulates the concept by signing the plaintext and then encrypting the payload before storage.",
            "IP Security protects traffic at the network layer: ESP encrypts payloads and AH validates packet integrity.",
        ],
    },
    {
        "id": "module-6",
        "title": "Module 6: Web Security",
        "summary": "Secure web communication depends on both transport protection and safe application design.",
        "points": [
            "SSL/TLS protects data in transit between the browser and server and should be enabled in production with HTTPS.",
            "CSRF tokens, input validation, secure cookies, and session expiry reduce common web attack paths.",
            "This project uses server-side validation, CSRF protection, and secure Flask session settings to demonstrate these ideas.",
        ],
    },
]


ACCESS_CONTROL_MATRIX = [
    {"resource": "Admin panel", "admin": "Read / Write", "staff": "No access"},
    {"resource": "Own inbox", "admin": "Read / Write", "staff": "Read / Write"},
    {"resource": "Other users' encrypted content", "admin": "Metadata only", "staff": "No access"},
    {"resource": "File uploads sent to you", "admin": "Read / Write", "staff": "Read / Write"},
    {"resource": "Activity logs", "admin": "Read", "staff": "Own actions only"},
]
