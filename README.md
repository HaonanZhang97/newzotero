# AI Research Note Platform

A full-stack web application designed for managing and searching research paper notes using semantic embeddings. Users can add papers via manual entry, file upload, or DOI search, and create AI-searchable excerpts and freeform notes.

🌐 **Live Demo**: [http://94.72.121.125:3000/](http://94.72.121.125:3000/)

---

## ✨ Features

- 📄 Add papers via:
  - Manual entry
  - File upload (PDF)
  - DOI-based lookup
- 🧠 Semantic search across:
  - Extracted excerpts
  - Freeform user notes
- 🔍 Vector embedding-based retrieval using language models
- 📥 Download uploaded PDF files directly from the interface
- 🧰 Fully Dockerized and deployable via `docker-compose`

---

## 🛠 Tech Stack

| Layer      | Technology           |
|------------|----------------------|
| Frontend   | Next.js (React)      |
| Backend    | Flask (RESTful API)  |
| Embedding  | Vector model (e.g. OpenAI / DeepSeek / Sentence Transformers) |
| Deployment | Docker, Docker Compose |
| Server     | Ubuntu (public IP: `94.72.121.125`) |

---

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose

### Run With Docker Compose

- docker-compose docker-compose.simple.yml up -d

### Clone the Repository

```bash
git clone https://github.com/your-username/ai-note-platform.git
cd ai-note-platform


