# Security

## Reporting a vulnerability

Do not open a public issue with exploitable details. Email the repository
maintainers or use GitHub's private security advisory channel. Include the
version, reproduction steps and impact.

## Supported versions

Only the `main` branch receives security fixes.

## Deployment checklist

- [ ] `SECRET_KEY` and `JWT_SECRET_KEY` are different, random (32 bytes) and out of git.
- [ ] `FLASK_DEBUG=0` and `FLASK_ENV=production`.
- [ ] HTTPS is mandatory; serve the frontend and API on the same domain or with a narrow CORS allowlist.
- [ ] `CORS_ORIGINS` contains the exact allowed domains (never `*`).
- [ ] `RATELIMIT_STORAGE_URI` points to Redis when running more than one worker.
- [ ] SMTP and provider credentials have been rotated and live in environment variables.
- [ ] `flask db upgrade` runs before the application starts.
- [ ] Database and `storage/uploads` backups are configured.
- [ ] `pip-audit -r backend/requirements.txt` and `npm audit --omit=dev` report no high findings.
- [ ] Verify that `.env` is not in the repository or in Docker images.
- [ ] Run `flask purge-tokens` periodically (cron) to clean the blacklist.

## Implemented controls

- HS256 JWTs with `iss`, `jti`, `iat`, `exp` and a per-user token version.
- Access tokens valid for 1 day and refresh tokens for 7 days, both configurable.
- Refresh rotation and a `jti` blacklist with expiration and purging.
- All sessions are invalidated when the password is changed or reset.
- Rate limiting on login, registration, recovery and password changes.
- bcrypt password hashing with a configurable minimum length.
- Password recovery with a random token, SHA-256 hashing and expiration.
- Generic responses to prevent user and email enumeration.
- Public registration disabled by default.
- User listing restricted to administrators.
- Uploads with cryptographic names, size limits and content validation.
- Security headers and JSON errors without internal stack traces.
- CORS allowlist and `SameSite=Lax` frontend cookies.
