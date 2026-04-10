# Deployment Guide

This document outlines the steps and best practices for deploying the Secure Communication Platform in a production environment. Please note that the main `README.md` covers local development and academic demonstration setups.

## 1. Important Production Considerations

Before deploying, ensure you understand the following changes required for a production environment:

- **Never use the built-in Flask development server** (`app.run()`) in production. Use a production-grade WSGI server like Gunicorn (Linux) or Waitress (Windows).
- **Enforce HTTPS.** All communications must be encrypted in transit using TLS/SSL.
- **Generate strong, unique secrets** for your environment variables.
- **Secure your MongoDB instance** with authentication, role-based access control, and network isolation.

## 2. Environment Variables

Create a `.env` file in the project root with strong, cryptographically secure random strings. 

```env
# Flask session signing key (keep this secret!)
FLASK_SECRET_KEY=your-super-strong-random-flask-secret

# Secret used to wrap private RSA keys in the database
PRIVATE_KEY_WRAP_SECRET=your-super-strong-random-wrap-secret

# Production MongoDB Connection String (with authentication)
MONGO_URI=mongodb://username:password@db-host:27017/secure_ngo_platform?authSource=admin

# Enforce secure cookies (Requires HTTPS)
ENABLE_HTTPS_ONLY=true
```

## 3. Web Server & WSGI Setup (Linux Example)

### Prerequisites

- Python 3.11+
- Nginx
- A valid SSL Certificate (e.g., Let's Encrypt / Certbot)

### Step 3.1: Install Dependencies and Gunicorn

Activate your virtual environment and install the required packages, plus Gunicorn:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Step 3.2: Run with Gunicorn

Test the application using Gunicorn:

```bash
gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
```

### Step 3.3: Set Up a Systemd Service

Create a systemd service to keep the application running in the background.

`sudo nano /etc/systemd/system/secure-ngo.service`

```ini
[Unit]
Description=Gunicorn instance to serve Secure NGO Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Data and information security
Environment="PATH=/path/to/Data and information security/.venv/bin"
ExecStart=/path/to/Data and information security/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start secure-ngo
sudo systemctl enable secure-ngo
```

### Step 3.4: Set Up Nginx Reverse Proxy

Configure Nginx to handle external HTTPS requests and proxy them to Gunicorn.

`sudo nano /etc/nginx/sites-available/secure-ngo`

```nginx
server {
    listen 80;
    server_name secure.your-ngo-domain.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name secure.your-ngo-domain.org;

    ssl_certificate /etc/letsencrypt/live/secure.your-ngo-domain.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/secure.your-ngo-domain.org/privkey.pem;

    # Recommended Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase max body size if you expect large secure file uploads
    client_max_body_size 15M;
}
```

Enable the configuration and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/secure-ngo /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 4. Docker Deployment (Optional)

In the future, you can containerize the application to make deployments easier. A standard deployment would look like:

1. Create a `Dockerfile` that installs requirements and runs Gunicorn.
2. Create a `docker-compose.yml` that provisions a MongoDB container alongside the Flask container.
3. Use an Nginx reverse proxy container or a cloud load balancer to handle HTTPS termination.

## 5. Security Post-Deployment Checks

- [ ] Ensure `ENABLE_HTTPS_ONLY=true` is set to enforce secure cookies.
- [ ] Verify that navigating to `http://` auto-redirects to `https://`.
- [ ] Ensure MongoDB port (27017) is blocked from external access via an OS firewall (e.g., UFW) or cloud security groups.
- [ ] Regularly monitor `activity_logs` in the admin panel for suspicious login attempts.
- [ ] Set up log rotation for both Nginx and Gunicorn to prevent disk exhaustion.