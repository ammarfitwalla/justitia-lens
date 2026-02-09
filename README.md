# Justitia Lens

<p align="center">
  <strong>AI-Powered Forensic Auditor for Criminal Justice</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gemini-3.0_Flash-blue?style=for-the-badge&logo=google" alt="Gemini 3.0">
  <img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js" alt="Next.js">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi" alt="FastAPI">
</p>

---

## 🔍 What is Justitia Lens?

**Justitia Lens** is an AI forensic auditor that automatically cross-references police reports with visual evidence to flag discrepancies. It reads case narratives (PDFs) and analyzes crime scene photos simultaneously, then highlights where the written account differs from the visual facts.

### The Problem
Discrepancies between police reports and bodycam/photo evidence often go unnoticed due to the sheer volume of data, leading to wrongful convictions or acquittals. Manual review is slow, expensive, and prone to human error.

### The Solution
Justitia Lens uses **Google Gemini 3.0 Flash** as an "objective second pair of eyes" — extracting claims from text, indexing visual evidence independently, and then synthesizing both to produce an audit report.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Narrative Analysis** | Extracts structured timelines from police reports (PDF/text) |
| **Vision Analysis** | Indexes objective visual facts from crime scene images |
| **Discrepancy Detection** | Cross-references narrative claims with visual evidence |
| **Timestamp Verification** | Pinpoints exactly when narratives diverge from visual evidence |
| **Structured JSON Output** | Ensures accuracy with Gemini's JSON mode |

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React, TailwindCSS |
| **Backend** | FastAPI, Python 3.10+ |
| **AI Model** | Google Gemini 3.0 Flash |
| **Database** | Supabase (PostgreSQL) |
| **Deployment** | Netlify (Frontend), Google Cloud Run (Backend) |

---

## 📁 Project Structure

```
justitia-lens/
├── frontend/          # Next.js web application
├── backend/           # FastAPI server + AI agents
├── docs/              # Documentation
├── media/             # Screenshots and assets
└── README.md          # You are here
```

---

## 🛠️ Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- Google AI Studio API Key

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=your_database_url
```

---

## 🎯 How It Works

1. **Upload Case** — User uploads a police report (PDF) and crime scene images
2. **Narrative Analysis** — AI extracts claims and builds a timeline
3. **Vision Analysis** — AI indexes visual facts from each image
4. **Synthesis** — AI cross-references both sources and flags discrepancies
5. **Report** — Clean, verifiable audit report with citations

---

## 🔮 Future Roadmap

- [ ] **Video Analysis** — Process bodycam footage with Gemini's video understanding
- [ ] **Citation Links** — Every AI claim links back to the specific text/pixel
- [ ] **Multi-language Support** — Analyze reports in multiple languages
- [ ] **Batch Processing** — Analyze multiple cases in parallel

---

## 📄 License

This project was built for the Google DeepMind Hackathon 2026.

---

<p align="center">
  <strong>Built with ❤️ using Google Gemini 3.0 Flash</strong>
</p>
