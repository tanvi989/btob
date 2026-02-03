# Backend Deployment Guide — End-to-End

Complete step-by-step guide to deploy this FastAPI backend on a Linux server and connect it to your domain with HTTPS.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Server Preparation](#2-server-preparation)
3. [Install System Packages](#3-install-system-packages)
4. [Point Your Domain to the Server](#4-point-your-domain-to-the-server)
5. [Upload or Clone the Backend Code](#5-upload-or-clone-the-backend-code)
6. [Python Virtual Environment and Dependencies](#6-python-virtual-environment-and-dependencies)
7. [Download MediaPipe Model](#7-download-mediapipe-model)
8. [Configure Environment Variables (.env)](#8-configure-environment-variables-env)
9. [Test the Backend Manually](#9-test-the-backend-manually)
10. [Run as a System Service (systemd)](#10-run-as-a-system-service-systemd)
11. [Install and Configure Nginx](#11-install-and-configure-nginx)
12. [Enable HTTPS with Let's Encrypt](#12-enable-https-with-lets-encrypt)
13. [Optional: Restrict CORS for Production](#13-optional-restrict-cors-for-production)
14. [Summary Checklist](#14-summary-checklist)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Prerequisites

Before you start, ensure you have:

| Item | Description |
|------|-------------|
| **Server** | A Linux VPS (Ubuntu 20.04 or 22.04 recommended). Can be from GCP Compute Engine, DigitalOcean, Linode, AWS EC2, etc. |
| **SSH access** | You can log in with `ssh user@your-server-ip`. |
| **Domain name** | A domain or subdomain you control (e.g. `api.yourdomain.com` or `vtob.yourdomain.com`). |
| **Static IP** | Your server has a **static/reserved public IP** so the domain can point to it. (On GCP: reserve a static external IP and attach it to the VM.) |

---

## 2. Server Preparation

### 2.1 Log in via SSH

```bash
ssh your_username@YOUR_SERVER_IP
```

### 2.2 Update the system

```bash
sudo apt update
sudo apt upgrade -y
```

### 2.3 (Optional) Create a dedicated user

If you prefer not to use `root` or the default user:

```bash
sudo adduser appuser
sudo usermod -aG sudo appuser
# Log out and log in as appuser if you use this
```

### 2.4 Open firewall ports

Allow HTTP (80) and HTTPS (443) so Nginx can serve your domain:

```bash
sudo ufw allow 22/tcp    # SSH — keep this
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
sudo ufw status
```

---

## 3. Install System Packages

Install Python 3.10+, Nginx, Certbot, and libraries needed for the app (e.g. OpenCV/MediaPipe):

```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip nginx certbot python3-certbot-nginx

# System libraries used by OpenCV/MediaPipe
sudo apt install -y libgl1-mesa-glx libglib2.0-0
```

Verify Python:

```bash
python3.10 --version
# Should show Python 3.10.x or higher
```

---

## 4. Point Your Domain to the Server

### 4.1 Get your server’s public IP

On the server or from your cloud console, note the **public IP** (e.g. `34.123.45.67`).

### 4.2 Add a DNS A record

At your domain registrar or DNS provider (e.g. GoDaddy, Namecheap, Cloudflare, Google Cloud DNS):

1. Open **DNS management** for your domain.
2. Add an **A** record:
   - **Type:** A  
   - **Name/Host:**  
     - Use `api` for `api.yourdomain.com`  
     - Or `vtob` for `vtob.yourdomain.com`  
     - Or `@` for `yourdomain.com`
   - **Value:** your server’s public IP  
   - **TTL:** 300 (or default)

### 4.3 Verify DNS

Wait a few minutes, then from your local machine:

```bash
ping api.yourdomain.com
# Replace with your actual hostname; it should resolve to your server IP
```

Or:

```bash
nslookup api.yourdomain.com
```

Once the domain resolves to your server IP, continue.

---

## 5. Upload or Clone the Backend Code

Choose one method.

### Option A: Create directory and clone with Git

```bash
sudo mkdir -p /var/www/backend
sudo chown $USER:$USER /var/www/backend
cd /var/www/backend

git clone https://github.com/YOUR_ORG/YOUR_REPO.git .
# Or clone the specific backend repo you use; adjust URL accordingly
```

### Option B: Upload with SCP (from your local machine)

On your **local** machine (Windows PowerShell or Git Bash):

```powershell
scp -r "C:\Users\ADMIN\Desktop\feb\vto\mf_backend-main\mf_backend-main\*" your_username@YOUR_SERVER_IP:/var/www/backend/
```

On the server, create the directory first if needed:

```bash
sudo mkdir -p /var/www/backend
sudo chown $USER:$USER /var/www/backend
```

Then run the `scp` from your PC. After upload, on the server:

```bash
cd /var/www/backend
ls -la
# You should see app/, requirements.txt, run_server.py, etc.
```

**Important:** Do **not** upload the `.env` file or `secrets/` in a way that commits them. Create `.env` and upload secrets securely on the server (see Step 8).

---

## 6. Python Virtual Environment and Dependencies

From the backend directory:

```bash
cd /var/www/backend

# Create virtual environment
python3.10 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (this may take several minutes; includes torch, opencv, etc.)
pip install -r requirements.txt
```

If you get errors about missing system packages, install them, e.g.:

```bash
sudo apt install -y build-essential python3.10-dev
```

Then run `pip install -r requirements.txt` again.

---

## 7. Download MediaPipe Model

The app expects the MediaPipe face landmarker model at `app/models/face_landmarker.task`. Download it on the server:

```bash
cd /var/www/backend
mkdir -p app/models
wget -O app/models/face_landmarker.task \
  https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

Verify:

```bash
ls -la app/models/face_landmarker.task
```

---

## 8. Configure Environment Variables (.env)

Create a `.env` file in the backend root. **Never commit this file or share it.**

```bash
cd /var/www/backend
nano .env
```

Add the following (replace with your real values):

```env
# Google Cloud Storage (path to service account JSON on this server)
GOOGLE_APPLICATION_CREDENTIALS=/var/www/backend/secrets/gcs-service-account.json
BUCKET_NAME=your-gcs-bucket-name
FOLDER_NAME=your-folder-name
GCP_PROJECT_ID=your-gcp-project-id

# MongoDB
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DB_NAME=your-database-name

# Gemini (optional but used by some features)
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_API_KEY=your-google-api-key
```

Save and exit (`Ctrl+O`, Enter, `Ctrl+X`).

### Upload secrets (GCS service account)

The app needs a GCP service account JSON for Google Cloud Storage:

1. On your local machine, ensure you have the JSON key file (e.g. `gcs-service-account.json`).
2. On the server, create the directory and set permissions:

```bash
mkdir -p /var/www/backend/secrets
chmod 700 /var/www/backend/secrets
```

3. From your **local** machine, upload the key (replace paths and host as needed):

```powershell
scp "C:\path\to\gcs-service-account.json" your_username@YOUR_SERVER_IP:/var/www/backend/secrets/
```

4. On the server, restrict the file:

```bash
chmod 600 /var/www/backend/secrets/gcs-service-account.json
```

Ensure the path in `.env` (`GOOGLE_APPLICATION_CREDENTIALS`) matches this file path.

---

## 9. Test the Backend Manually

Run the app in the foreground to confirm it starts and responds:

```bash
cd /var/www/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

You should see something like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

In another SSH session (or from the server):

```bash
curl http://127.0.0.1:8000/
# Expected: {"message":"API running"}
```

If you see that, the backend is working. Press `Ctrl+C` to stop it. We’ll run it permanently with systemd next.

---

## 10. Run as a System Service (systemd)

So the backend runs on boot and restarts if it crashes:

### 10.1 Create the service file

```bash
sudo nano /etc/systemd/system/mf-backend.service
```

Paste the following. **Adjust paths if your app is not in `/var/www/backend`.**

```ini
[Unit]
Description=MF Backend (FastAPI)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/backend
Environment="PATH=/var/www/backend/venv/bin"
ExecStart=/var/www/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

If you use a different user (e.g. `ubuntu`), change `User=` and `Group=` to that user.

### 10.2 Set ownership

So the `www-data` user can read the app and `.env`:

```bash
sudo chown -R www-data:www-data /var/www/backend
```

If you use another user, e.g. `ubuntu`:

```bash
sudo chown -R ubuntu:ubuntu /var/www/backend
```

And in the service file set `User=ubuntu` and `Group=ubuntu`.

### 10.3 Start and enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable mf-backend
sudo systemctl start mf-backend
sudo systemctl status mf-backend
```

You should see `active (running)`. The API is now listening on `http://127.0.0.1:8000` on the server.

---

## 11. Install and Configure Nginx

Nginx will accept requests on your domain and forward them to the backend on port 8000.

### 11.1 Create site configuration

Use your actual domain name (e.g. `api.yourdomain.com`):

```bash
sudo nano /etc/nginx/sites-available/mf-backend
```

Paste (replace `api.yourdomain.com` with your domain):

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 11.2 Enable the site and test Nginx

```bash
sudo ln -s /etc/nginx/sites-available/mf-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 11.3 Test via domain (HTTP)

From your browser or local machine:

```
http://api.yourdomain.com/
```

You should see `{"message":"API running"}`. Swagger docs:

```
http://api.yourdomain.com/docs
```

---

## 12. Enable HTTPS with Let's Encrypt

Certbot will get a free SSL certificate and configure Nginx.

### 12.1 Run Certbot

Replace `api.yourdomain.com` with your domain:

```bash
sudo certbot --nginx -d api.yourdomain.com
```

Follow the prompts:

- Enter your email for renewal notices.
- Agree to terms of service.
- Choose whether to redirect HTTP to HTTPS (recommended: **Yes**).

### 12.2 Verify HTTPS

Open:

```
https://api.yourdomain.com/
```

You should see the same JSON response over HTTPS. Certbot automatically renews certificates; you can test renewal with:

```bash
sudo certbot renew --dry-run
```

---

## 13. Optional: Restrict CORS for Production

To allow only your frontend domain to call the API, edit the backend:

```bash
nano /var/www/backend/app/main.py
```

Find the CORS middleware and change `allow_origins`:

```python
# From:
allow_origins=["*"],

# To (use your real frontend domain):
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
],
```

Then restart the backend:

```bash
sudo systemctl restart mf-backend
```

---

## 14. Summary Checklist

| Step | Action |
|------|--------|
| 1 | Server with static IP; SSH access |
| 2 | `apt update && apt upgrade`; open ports 80, 443 |
| 3 | Install Python 3.10+, nginx, certbot, libgl1-mesa-glx, libglib2.0-0 |
| 4 | DNS: A record for your domain → server IP; verify with `ping` |
| 5 | Create `/var/www/backend`; clone or upload backend code |
| 6 | `python3.10 -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt` |
| 7 | Download `face_landmarker.task` into `app/models/` |
| 8 | Create `.env`; upload GCS key to `secrets/`; set permissions |
| 9 | Test: `uvicorn app.main:app --host 127.0.0.1 --port 8000` and `curl http://127.0.0.1:8000/` |
| 10 | Create `mf-backend.service`; `chown` app to service user; enable and start service |
| 11 | Nginx site for your domain → `proxy_pass http://127.0.0.1:8000`; enable site; `nginx -t`; reload nginx |
| 12 | `certbot --nginx -d your-domain` for HTTPS |
| 13 | (Optional) Restrict CORS in `app/main.py` and restart backend |

**URLs after deployment:**

- API root: `https://api.yourdomain.com/`
- Swagger docs: `https://api.yourdomain.com/docs`
- ReDoc: `https://api.yourdomain.com/redoc`

---

## 15. Troubleshooting

### Backend won’t start (`systemctl status mf-backend` shows failed)

- Check logs: `sudo journalctl -u mf-backend -n 50 --no-pager`
- Ensure paths in the service file match your install (`WorkingDirectory`, `ExecStart`).
- Ensure `app/models/face_landmarker.task` exists.
- Run manually: `cd /var/www/backend && source venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000` and read the error.

### 502 Bad Gateway from Nginx

- Backend must be listening on `127.0.0.1:8000`. Check: `curl http://127.0.0.1:8000/` on the server.
- Restart backend: `sudo systemctl restart mf-backend`.

### Domain not resolving

- Wait for DNS (up to 48 hours, often minutes). Use `nslookup your-domain`.
- Confirm the A record points to the correct server IP.

### SSL certificate errors

- Ensure port 80 is open and Nginx is running so Certbot can complete the challenge.
- Run `sudo certbot --nginx -d your-domain` again and follow any error messages.

### Permission denied on `.env` or `secrets/`

- Service user (e.g. `www-data`) must be able to read the app directory:  
  `sudo chown -R www-data:www-data /var/www/backend`

---

**Running locally (unchanged):**

```bash
cd /path/to/mf_backend-main/mf_backend-main
# Create .env with the same variables
python run_server.py
# API: http://127.0.0.1:8000
```
