# 📅 Timetable AI & Conflict Resolution Studio

A modern Flask + SQLite application containerized with **Docker** and powered by **Google Gemini AI** (`gemini-3.6-flash`) to assist academic coordinators in managing, simulating, optimizing, and resolving college timetable schedules.

---

## 🌟 Features

- **✨ Gemini AI Assistant**: Ask natural language questions, request intelligent schedule optimizations, and receive real-time reasoning powered by `gemini-3.6-flash`.
- **📅 Real College Dataset**: Pre-seeded with **MLR Institute of Technology (B.Tech CSD-C, AK-204)** faculty, labs, rooms, and weekly schedule.
- **🔄 Change Simulator**: Test schedule changes virtually with automatic self-conflict exemption and Gemini AI reasoning.
- **☀️ Light & Clean UI**: White theme with high contrast slate typography, custom color badges, and responsive card layouts.
- **🚀 Production Ready**: Containerized backend with Gunicorn WSGI multi-worker process deployment.

---

## 🛠️ Step-by-Step Deployment Guide

### Option 1: Deploy Locally or on a Virtual Private Server (VPS) via Docker (Recommended)

#### Prerequisites
- Installed [Docker](https://www.docker.com/) and Docker Compose.

#### Steps:
1. **Clone or Open Project Directory**:
   ```bash
   cd Timetable
   ```

2. **Configure Environment Variables**:
   Create or edit the `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=5000
   ```

3. **Deploy with Docker Compose**:
   Run the following command to build and launch the production container in detached mode:
   ```bash
   docker compose up -d --build
   ```

4. **Access your Web Application**:
   Open your browser at:
   ```
   http://localhost:5000
   ```
   *(Or `http://<your-vps-ip>:5000` if deploying on AWS/DigitalOcean).*

5. **Stop or Restart Deployment**:
   - Restart: `docker compose restart`
   - Stop: `docker compose down`

---

### Option 2: Deploy to Render.com (Free Cloud Hosting)

1. Push your project code to a **GitHub** or **GitLab** repository.
2. Sign up at [Render.com](https://render.com/).
3. Click **New +** ➔ Select **Web Service**.
4. Connect your GitHub repository.
5. Set runtime environment:
   - **Environment**: `Docker`
   - **Region**: Select your preferred region.
6. Under **Environment Variables**, add:
   - Key: `GEMINI_API_KEY` | Value: `your_gemini_api_key`
7. Click **Create Web Service**. Render will automatically build the `Dockerfile` and give you a public URL (`https://your-app.onrender.com`).

---

### Option 3: Deploy to Railway.app

1. Install the Railway CLI or connect via GitHub at [Railway.app](https://railway.app/).
2. Run in terminal:
   ```bash
   railway login
   railway init
   railway up
   ```
3. Add variable `GEMINI_API_KEY` under your Railway service settings.
4. Generate a public domain in Railway settings.

---

### Option 4: Deploy to Fly.io

1. Install Fly CLI ([flyctl](https://fly.io/docs/hands-on/install-flyctl/)).
2. Run:
   ```bash
   fly launch
   fly secrets set GEMINI_API_KEY="your_api_key"
   fly deploy
   ```

---

## 🧪 Verification Commands

- Check running containers:
  ```bash
  docker compose ps
  ```
- View live production server logs:
  ```bash
  docker logs -f timetable-production
  ```