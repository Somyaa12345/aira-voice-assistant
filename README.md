# 🎙️ Aira — Local-First Personal Voice Assistant

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%7C%20Llama3.2-orange.svg)](https://ollama.ai/)
[![Faster-Whisper](https://img.shields.io/badge/STT-Faster--Whisper-green.svg)](https://github.com/SYSTRAN/faster-whisper)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Aira** is a privacy-focused, ultra-low-latency, local-first personal voice assistant built with **Python, FastAPI, Ollama (Llama 3.2), Faster-Whisper, and SQLite**.

Designed to run completely offline on edge hardware without sending user audio or data to cloud servers.

---

## ✨ Features

- ⚡ **Sub-Second Latency**: Fast-path intent engine delivers sub-300ms response times for time, date, math, search, and app launching.
- 🎙️ **Local Speech-to-Text (STT)**: Embedded `Faster-Whisper` running `tiny`/`base` models on local CPU with auto-container header detection (`.webm` Opus / `.wav`).
- 🧠 **Local LLM Intelligence**: Powered by Ollama (`llama3.2:1b`), retaining model warm-state in RAM (`keep_alive: 60m`) for instant zero-latency responses.
- 🗣️ **Natural Female Voice Persona**: High-quality Indian English speech synthesis with custom pitch and fluid conversational rate.
- 🛠️ **Desktop Tool Calling**: Launch YouTube songs, open Spotify, search Google, perform calculations, and run browser widgets hands-free.
- 💾 **Long-Term SQLite Memory**: Remembers user identity (*Somya*), notes, reminders, and conversation history across restarts.
- 🎨 **Modern Dark Web UI**: Cyberpunk glow interface featuring dynamic audio visualizer orb, click-to-open tool badges, and live status feedback.

---

## 🏗️ Architecture Flow

```text
  ┌─────────────────┐
  │   Microphone    │
  └────────┬────────┘
           │ (WebM/WAV Audio Stream)
           ▼
  ┌─────────────────┐
  │   Frontend UI   │ ──(Web Speech Synthesis Female Voice Output)
  └────────┬────────┘
           │ (REST POST /api/voice/process)
           ▼
┌────────────────────────────────────────────────────────┐
│                   Aira FastAPI Backend                 │
│                                                        │
│  1. Audio Handler   ──► Container Header & PCM Decoder  │
│  2. Faster-Whisper  ──► Local CPU Speech Transcription │
│  3. Intent Engine   ──► Fast Sub-100ms Action Router   │
│  4. Ollama LLM      ──► Local Llama3.2 Response        │
│  5. SQLite Database ──► Memories, Notes & History      │
│  6. Tool Registry   ──► YouTube/Spotify/Math/Search    │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### Prerequisites

1. **Python 3.10+** installed.
2. **Ollama** installed and running locally:
   ```bash
   ollama pull llama3.2:1b
   ```

### 1. Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Somyaa12345/aira-voice-assistant.git
cd aira-voice-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env`:

```env
APP_NAME="Aira Voice Assistant"
DEBUG=True
HOST=127.0.0.1
PORT=8000

OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2:1b"

WHISPER_MODEL_SIZE="tiny"
WHISPER_DEVICE="cpu"
WHISPER_LANGUAGE="en"

DATABASE_URL="sqlite:///./aira.db"
```

### 3. Run the Backend Server

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open your browser and navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**!

---

## 🐳 Docker Deployment

You can run Aira via Docker Compose:

```bash
docker-compose up --build
```

This starts:
- **Aira Assistant**: `http://localhost:8000`
- **Ollama LLM Engine**: `http://localhost:11434`
- **LiveKit Server**: `ws://localhost:7880`

---

## 🛠️ API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/chat` | `POST` | Process text query through LLM, memory & tool engine |
| `/api/voice/process` | `POST` | Upload audio blob (WebM/WAV) → STT → Process intent → JSON reply |
| `/api/memory/memories` | `GET` / `POST` | View or store long-term SQLite memories |
| `/api/memory/notes` | `GET` / `POST` | Manage user notes |
| `/api/memory/reminders` | `GET` / `POST` | Manage user reminders |
| `/api/tools/execute` | `POST` | Manually trigger a desktop tool |
| `/api/health` | `GET` | Healthcheck endpoint |

---

## 🧪 Running Tests

Run the master automated test suite:

```bash
python backend/scripts/run_all_tests.py
```

---

## 👩‍💻 Author

Developed with ❤️ by **[Somya](https://github.com/Somyaa12345)**.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
