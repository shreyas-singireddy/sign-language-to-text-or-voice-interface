# SignBridge AI

An AI-powered web application for translating American Sign Language (ASL) hand gestures into text and speech in real time.

## Project Structure

- `frontend/` — Vite + React + Tailwind UI
- `backend/` — FastAPI backend with MongoDB Atlas, JWT auth, and AI/Computer Vision utilities
- `docker-compose.yml` — local development container orchestration

## Quick Start

1. Set environment variables in `backend/.env`:
   - `MONGO_URI`
   - `JWT_SECRET`
2. Install backend dependencies:
   ```bash
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```
4. Run backend:
   ```bash
   cd ../backend
   .\.venv\Scripts\activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Run frontend:
   ```bash
   cd ../frontend
   npm run dev -- --host 0.0.0.0 --port 4173
   ```

## Features

- Real-time ASL translation
- Webcam-based gesture capture
- JWT authentication with protected routes
- Admin analytics dashboard
- Translation history and export controls
- Dark/light mode and accessibility-first design
- MediaPipe / TensorFlow integration stubs

## API Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/reset-password`
- `POST /api/translate`
- `GET /api/history`
- `DELETE /api/history/{id}`
- `GET /api/admin/users`
- `GET /api/admin/analytics`
- `GET /api/admin/translations`
