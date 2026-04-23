# 🚀 RAG Micro API — Deployment Guide

## 📌 Overview

This document describes the deployment process for the **RAG Micro API**, a FastAPI-based service designed for:

* Retrieval-Augmented Generation (RAG)
* PCB defect analysis
* Standards-grounded report generation

The system is containerized using **Docker** and deployed with **Docker Compose**, with **Nginx** acting as a reverse proxy.

---

## 🧱 Architecture

```cwd
Client → Nginx → FastAPI (Gunicorn + Uvicorn)
                        ↓
                External Services
                - Qdrant (Vector DB)
                - Voyage AI (Embeddings)
                - Gemini API (LLM)
```

---

## 📂 Project Structure

```text
project-root/
├── app/
├── data/
│   └── metrics/
├── nginx/
│   └── default.conf
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── .dockerignore
└── README.md
```

---

## ⚙️ Requirements

### Local (Windows / Linux)

* Docker Desktop (Windows) or Docker Engine (Linux)
* Docker Compose

### VPS (Ubuntu recommended)

* Ubuntu 22.04+
* Docker + Docker Compose plugin

---

## 🔐 Environment Configuration

Create a `.env` file based on `.env.example`.

### Example

```env
APP_NAME=rag-microapi
APP_ENV=production
APP_VERSION=0.2.0
API_PREFIX=/api/v1

USE_MOCK_PROVIDERS=false

QDRANT_URL=http://YOUR_QDRANT_HOST:6333
QDRANT_API_KEY=YOUR_QDRANT_API_KEY
QDRANT_COLLECTION=dev

VOYAGE_API_KEY=YOUR_VOYAGE_API_KEY
VOYAGE_MODEL=voyage-4-lite

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash-lite

HTTP_TIMEOUT_SECONDS=45
```

⚠️ **Important:** Never commit `.env` to version control.

---

## 🐳 Docker Deployment

### 1. Build and Run

```bash
docker compose up -d --build
```

### 2. Check Containers

```bash
docker compose ps
```

### 3. View Logs

```bash
docker compose logs -f
```

---

## 🌐 API Access

Once running:

| Endpoint          | URL                                       |
| ----------------- | ----------------------------------------- |
| Health Check      | <http://localhost/api/v1/health>          |
| API Docs          | <http://localhost/docs>                   |
| Report Generation | <http://localhost/api/v1/report/generate> |
| Metrics           | <http://localhost/api/v1/report/metrics>  |

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost/api/v1/health
```

### Example POST Request

```bash
curl -X POST http://localhost/api/v1/report/generate \
-H "Content-Type: application/json" \
-d '{
  "detections": [
    {
      "severity": "HIGH",
      "defect_class": "short_circuit",
      "confidence": 0.96,
      "location": "lower-right",
      "width_mm": 2.14,
      "height_mm": 0.61,
      "area_mm2": 1.30,
      "reference": "IPC-A-600"
    }
  ],
  "standard_target": "IPC-A-600"
}'
```

---

## ☁️ VPS Deployment (Hetzner / Ubuntu)

### 1. Install Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
```

---

### 2. Upload Project

#### Option A: Git

```bash
git clone <repo>
cd <repo>
```

#### Option B: SCP (from Windows)

```powershell
scp -r . user@your_vps_ip:/home/user/rag-microapi
```

---

### 3. Setup Environment

```bash
cd rag-microapi
mkdir -p data/metrics
nano .env
```

---

### 4. Run Containers

```bash
docker compose up -d --build
```

---

### 5. Verify Deployment

```bash
curl http://localhost/api/v1/health
```

Then access from browser:

```link
http://YOUR_VPS_IP/docs
```

---

## 🔧 Nginx Configuration

The API is exposed via Nginx on port 80:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://api:8000;
    }
}
```

---

## 📊 Metrics

Metrics are stored locally:

```cmd
data/metrics/report_metrics.jsonl
```

Tracked metrics include:

* Grounding strength
* Interpretation type
* Acceptability status
* Latency
* Consistency rate

---

## ⚠️ Known Limitations

* Grounding depends on retrieval quality (Qdrant + indexing)
* IPC standards are partially implicit (not fully textual)
* Some defects may require engineering review

---

## 🔒 Security Considerations

* Do not expose API keys
* Use HTTPS in production (recommended)
* Restrict firewall ports (80 / 443 only)

---

## 🚀 Future Improvements

* HTTPS via Let's Encrypt
* CI/CD pipeline
* Improved chunking & retrieval
* Metadata-based filtering in Qdrant
* Hybrid rule-based + RAG reasoning

---

## 🧠 Final Notes

The system is designed to be:

* Deterministic and consistent
* Conservative in decision-making
* Grounded in industrial standards

This ensures reliability in real-world engineering workflows.

---

## 📞 Support

For issues:

* Check logs (`docker compose logs -f`)
* Validate `.env` variables
* Confirm connectivity to Qdrant and APIs

---

**Status:** Production-ready (v1)
**Maintained by:** RAG Micro API Team
