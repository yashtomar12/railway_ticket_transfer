# train_project

Railway Ticket Transfer System — Django project.

Quickstart

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set environment variables in `.env` or `settings.py` for:

- `GEMINI_API_KEY` — (optional) Google Gemini API key
- `OPENAI_API_KEY` — (optional) OpenAI API key (not required if using only Gemini)

3. Run migrations and start server:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Notes
- Static and media files are stored in `media/` (ignored in repo).
- Admin customizations are in `getticket/admin.py`.

