# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small Python chatbot API and its training script.

- `api.py`: FastAPI application. Loads `modelo_chatbot.pkl` and exposes `GET /` and `POST /chat`.
- `train_model.py`: Trains a scikit-learn text classification pipeline from `data.xlsx`.
- `data.xlsx`: Training dataset. Expected columns are `texto` and `intent`.
- `modelo_chatbot.pkl`: Generated trained model used by the API.
- `requirements.txt`: Runtime and training dependencies.
- `venv/` and `__pycache__/`: Local/generated directories. Do not edit or rely on them in code changes.

## Build, Test, and Development Commands

Create and activate a virtual environment before installing dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Retrain the chatbot model after changing `data.xlsx` or training logic:

```powershell
python train_model.py
```

Run the API locally:

```powershell
uvicorn api:app --reload
```

Then open `http://127.0.0.1:8000/docs` to exercise the endpoints through FastAPI's Swagger UI.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Keep module names lowercase with underscores when adding files, for example `model_utils.py`. Use descriptive Spanish or English names consistently within a file; avoid mixing both in the same new feature unless matching existing code. Keep API request and response fields explicit through Pydantic models.

Prefer small functions for reusable behavior, especially if model loading, validation, or response selection grows beyond `api.py`.

## Testing Guidelines

No automated tests are currently included. Add tests under a new `tests/` directory when changing API behavior or training logic. Use `pytest` naming conventions:

- Test files: `tests/test_api.py`
- Test functions: `test_chat_returns_intent()`

Recommended command after tests are added:

```powershell
pytest
```

For API changes, include at least one test for `GET /` and one for `POST /chat`.

## Commit & Pull Request Guidelines

This directory does not currently include Git history, so use concise imperative commit messages such as `Add chatbot API tests` or `Update training dataset`.

Pull requests should include a short description, the reason for the change, commands run, and any model or dataset changes. If API behavior changes, include example request/response JSON and note whether `modelo_chatbot.pkl` was regenerated.

## Security & Configuration Tips

Do not commit secrets, credentials, or private user data in `data.xlsx`. Treat `modelo_chatbot.pkl` as a generated artifact: regenerate it from trusted data and avoid loading pickle files from unknown sources.
