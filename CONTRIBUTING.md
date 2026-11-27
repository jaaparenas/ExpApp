# Contributing

## Environment

1. Backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   cp .env.example .env
   flask --app server db upgrade
   ```
2. Frontend:
   ```bash
   cd frontend/nuxt
   npm ci
   ```

## Before opening a PR

- Backend: `python -m unittest discover -s tests -p 'test*.py' -v`
- Frontend: `npm run build`
- E2E: `npm run test:e2e` with the backend and frontend running (see README).
- Security: `bandit -q -r app server.py config.py` and `pip-audit -r requirements.txt`.
- `pre-commit install` to validate whitespace, YAML and private keys.

## Rules

- Never commit `.env`, databases, uploaded files or secrets.
- Keep error responses in JSON and without internal stack traces.
- Add a test for every security fix or functional bug.
- English for documentation, comments and user-facing messages.
- Schema changes require a new migration (`flask db migrate`).

## Security reports

Do not open a public issue with exploitable details. See `SECURITY.md`.
