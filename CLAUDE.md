# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chatbot API about the game **Pou** (virtual pet). Combines a local scikit-learn intent classifier with rule-based keyword matching and an optional Groq LLM fallback for answers outside the local knowledge base.

## Commands

```bash
# Activate venv (PowerShell on Windows)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Retrain the model (produces modelo_chatbot.pkl)
python train_model.py

# Run the API (auto-reload)
uvicorn api:app --reload
# Swagger UI at http://127.0.0.1:8000/docs
```

## Architecture

**Response resolution order in `POST /chat`:**

1. `debe_consultar_groq_primero` — certain questions (age, multiplayer) go straight to Groq memory/API.
2. `respuesta_especifica` — keyword-based hardcoded answers (platforms, stats, mechanics).
3. `es_interaccion_basica` — greetings/farewells/thanks matched by exact set membership.
4. `buscar_en_memoria` — CSV cache (`memoria_groq.csv`) of prior Groq responses.
5. Groq LLM fallback — called when `GROQ_ALWAYS_FALLBACK=true` (default) or confidence < threshold.
6. `respuesta_fallback` — generic "I don't know" messages.

**Model pipeline (`train_model.py`):** TF-IDF vectorizer → Logistic Regression. Trained on `data.xlsx` (columns: `texto`, `intent`). Outputs `modelo_chatbot.pkl`.

**Key environment variables:**
- `GROQ_API_KEY` — enables Groq LLM fallback
- `GROQ_MODEL` — default `llama-3.3-70b-versatile`
- `CONFIDENCE_THRESHOLD` — default `0.55`; below this triggers Groq
- `GROQ_ALWAYS_FALLBACK` — default `true`; always tries Groq when local rules don't match

## Coding Conventions

- Python 3, 4-space indentation
- Spanish comments and response strings; code identifiers can mix Spanish/English matching existing style
- API fields use Pydantic models (`Mensaje`)
- Responses in Spanish, written without accents in hardcoded strings (normalizar strips diacritics for matching)

## Testing

No tests yet. When added, use `pytest` under a `tests/` directory.
