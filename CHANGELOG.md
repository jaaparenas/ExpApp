# Changelog

## 2.0.0 — 2026-11-27

### Security

- Removed hardcoded SMTP credentials and default keys; everything is read from `.env`.
- Rewrote the git history to remove secrets from every commit.
- Restricted `/1.0/user/users` to administrators.
- JWTs with `iss`, `jti`, expiration and token version; refresh rotation and revocation.
- Changing or resetting the password invalidates every session.
- Password recovery with a random token, SHA-256 hashing, expiration and generic responses.
- Rate limiting on login, registration, recovery, refresh and password changes.
- Public registration disabled by default.
- Uploads with cryptographic names, size limits and real content validation.
- CORS allowlist, security headers and JSON errors without stack traces.
- Authentication audit logs without sensitive data.

### Backend

- Flask 3, SQLAlchemy 2, PyJWT 2, Flask-Migrate 4 and Flask-Limiter.
- Flask CLI: `test`, `coverage`, `create-db`, `drop-db`, `create-su`, `purge-tokens`.
- Versioned initial migration and `flask db` commands.
- Pinned dependencies and separate development requirements.
- 28 unit tests.

### Frontend

- Migrated from Nuxt 2 (EOL) to Nuxt 4.7 + Vue 3.5.
- Removed the previous 203 npm vulnerabilities; 9 moderate build-tooling advisories remain.
- Auth with automatic refresh, es/en i18n and custom toasts.
- Login, dashboard, profile, users, upload, analytics, groups and reset pages.
- 10 headless Playwright E2E tests.

### Infrastructure

- Dockerfile with Gunicorn and an entrypoint that applies migrations.
- `docker-compose` with PostgreSQL, healthcheck and volumes.
- GitHub Actions CI for backend, migrations, bandit, pip-audit and frontend.
- Makefile, SECURITY.md, CONTRIBUTING.md and an updated README.

### License

- Changed from CC0 1.0 Universal to the MIT License; attribution is now required.
