ExpAPP
=====

A general-purpose template for building REST APIs with the common pieces
already solved: JWT authentication, role-based access, password recovery,
file uploads, rate limiting and a modern SPA frontend.

Current stack:

* **Backend:** Flask 3, SQLAlchemy 2, Flask-Migrate, PyJWT, Flask-Limiter,
  Flask-Bcrypt and SQLite/PostgreSQL.
* **Frontend:** Nuxt 4 (Vue 3), without heavy UI frameworks.
* **Testing:** unittest for the backend and **headless** Playwright for E2E.

The default branch is ``main``.


Requirements
------------

* Python 3.10 or newer.
* Node.js 22 LTS (recommended) or 24.11+.
* SQLite for development; PostgreSQL optional for production.
* Docker and Docker Compose (optional).


Backend
-------

1. Create and activate a virtual environment::

    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

2. Create the local configuration file::

    cp .env.example .env

3. Generate two different secrets::

    python -c "import secrets; print(secrets.token_hex(32))"

   Put them in ``SECRET_KEY`` and ``JWT_SECRET_KEY`` inside ``.env``.
   The ``.env`` file is ignored by git and **must never be committed**.

4. Apply migrations and create the superuser::

    flask --app server db upgrade
    flask --app server create-su

   ``create-su`` uses ``ADMIN_USERNAME``, ``ADMIN_EMAIL`` and
   ``ADMIN_PASSWORD``. If no password is set, it generates a random one and
   prints it once.

5. Start the API::

    flask --app server run --debug

   Available at ``http://localhost:5000``. Healthcheck: ``GET /health``.

6. Run the tests::

    python -m unittest discover -s tests -p 'test*.py' -v

Useful CLI commands::

    flask --app server db upgrade      # apply migrations
    flask --app server db migrate -m "change"
    flask --app server create-db       # development shortcut
    flask --app server drop-db
    flask --app server create-su
    flask --app server purge-tokens    # clean expired blacklist entries
    flask --app server test


Frontend
--------

::

    cd frontend/nuxt
    npm ci
    cp .env.example .env      # optional: NUXT_PUBLIC_API_BASE
    npm run dev -- --port 3000

The frontend runs at ``http://localhost:3000`` and calls the API defined in
``NUXT_PUBLIC_API_BASE`` (defaults to ``http://localhost:5000``).

Production::

    npm run build
    npm run preview


Headless E2E tests with Playwright
----------------------------------

1. Backend with a test database and rate limiting disabled::

    cd backend
    export DATABASE_URL=sqlite:////tmp/expapp-e2e.db
    export SECRET_KEY=e2e-secret
    export JWT_SECRET_KEY=e2e-jwt-secret
    export ADMIN_USERNAME=admin
    export ADMIN_EMAIL=admin@local.com
    export ADMIN_PASSWORD=admin12345
    export RATELIMIT_ENABLED=0
    flask --app server db upgrade
    flask --app server create-su
    flask --app server run --port 5000

2. Frontend in another terminal::

    cd frontend/nuxt
    npm run dev -- --port 3100

3. Install Chromium (first run only) and execute the tests::

    cd frontend/nuxt
    npx playwright install chromium
    npm run test:e2e

The suite covers login, logout, protected routes, profile, CSV upload,
rejection of fake files, user listing and password recovery links. Playwright
runs headless and never opens a visible window.


Docker Compose
--------------

1. Copy and fill in the variables::

    cp .env.example .env

   Set ``POSTGRES_PASSWORD``, ``SECRET_KEY`` and ``JWT_SECRET_KEY``.
2. Start the services::

    docker compose up --build

3. Create the superuser inside the container::

    docker compose exec backend flask --app server create-su

The API is served at ``http://localhost:5000`` and PostgreSQL data lives in
the ``dbdata`` volume. Uploaded files are stored in the ``uploads`` volume.


Main endpoints
--------------

==============================  ========  ===================================
Route                           Method    Description
==============================  ========  ===================================
``/``                           GET       Basic service information
``/health``                     GET       Healthcheck
``/1.0/user/login``             POST      Login; returns access + refresh
``/1.0/user/register``          POST      Registration (disabled by default)
``/1.0/user/data``              GET       Authenticated user profile
``/1.0/user/refresh``           POST      Rotate the refresh token
``/1.0/user/logout``            POST      Revoke access and refresh tokens
``/1.0/user/change_password``   POST      Change password and close sessions
``/1.0/user/reset_password_request``  POST  Request password recovery by email
``/1.0/user/reset_password/<token>``  GET/POST  Validate/update password
``/1.0/user/users``             GET/POST  Paginated listing (admin only)
``/1.0/datos/subir``            POST      File upload (authenticated)
==============================  ========  ===================================


Security
--------

* Secrets and mail credentials are read **only** from environment variables.
  The application refuses to start when ``SECRET_KEY`` or ``JWT_SECRET_KEY``
  are missing.
* JWTs include ``iss``, ``jti``, expiration and a per-user token version; the
  refresh token rotates and used tokens are revoked.
* Changing or resetting the password invalidates every session.
* Rate limiting on login, registration, recovery and password changes.
* Password recovery uses a random token, SHA-256 hashing and expiration.
* User listing is restricted to administrators.
* Uploads are renamed with ``secrets``, size-limited and validated by real
  content, not only by extension.
* Security headers, CORS allowlists and JSON errors without internal traces.

See ``SECURITY.md`` for the deployment checklist and ``PLAN.md`` for the
historical diagnosis and remaining tasks.


License
-------

This project is released under the **MIT License** (SPDX: ``MIT``).

You may use, copy, modify, distribute and sublicense it, including for
commercial purposes, provided that the copyright notice and this permission
notice are included in all copies or substantial portions of the Software.
In other words, **attribution to the original author is required**.

See the full text in ``LICENSE``.
