# BridgeEscrow V2 — Ubuntu Deployment Guide

This guide covers complete production deployment on Ubuntu 20.04, 22.04, or 24.04 LTS.

---

## 1. System Requirements & Package Installation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip mysql-server nginx certbot python3-certbot-nginx curl git

# Install Node.js 20 LTS (required by Vite 5)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## 2. Production Database Setup (MySQL)

```bash
sudo service mysql start

# Secure database and create dedicated bridgeescrow user
sudo mysql -e "CREATE DATABASE bridgeescrow_v2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'bridge'@'localhost' IDENTIFIED BY 'StrongProductionPasswordHere';"
sudo mysql -e "GRANT ALL PRIVILEGES ON bridgeescrow_v2.* TO 'bridge'@'localhost'; FLUSH PRIVILEGES;"
```

---

## 3. Backend Deployment

```bash
cd /opt/bridgeescrow-v2/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt

# Configure production environment
cp .env.example .env
nano .env
```

Ensure the following variables are configured in `backend/.env`:
```ini
DATABASE_URL=mysql+pymysql://bridge:StrongProductionPasswordHere@localhost:3306/bridgeescrow_v2
SECRET_KEY=generate-a-64-char-random-string
JWT_SECRET=generate-a-64-char-random-string
FLASK_RUN_PORT=5050
CORS_ORIGINS=https://your-domain.example

# Set live mode when Daraja credentials are approved
PAYMENT_MODE=simulated
SMS_MODE=simulated
```

Run database migrations:
```bash
flask --app wsgi db upgrade
```

---

## 4. Systemd Service for Backend

Create `/etc/systemd/system/bridgeescrow-backend.service`:
```ini
[Unit]
Description=BridgeEscrow V2 Backend Service
After=network.target mysql.service

[Service]
User=www-data
WorkingDirectory=/opt/bridgeescrow-v2/backend
EnvironmentFile=/opt/bridgeescrow-v2/backend/.env
ExecStart=/opt/bridgeescrow-v2/backend/.venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5050 wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bridgeescrow-backend
```

---

## 5. Frontend Production Build

```bash
cd /opt/bridgeescrow-v2/frontend
npm install
npm run build
```

This compiles static assets into `frontend/dist/`.

---

## 6. Nginx Reverse Proxy & SSL Configuration

Create `/etc/nginx/sites-available/bridgeescrow`:
```nginx
server {
    server_name your-domain.example;

    root /opt/bridgeescrow-v2/frontend/dist;
    index index.html;

    # Frontend Single Page App routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and acquire SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/bridgeescrow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.example
```

---

## 7. Docker Alternative Deployment

For containerized deployment, use the prepared files in `deploy/`:
```bash
cp deploy/production.env.example deploy/production.env
# Edit credentials in deploy/production.env
docker compose -f deploy/compose.yaml up -d --build
```
