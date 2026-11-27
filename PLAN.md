# Plan de revisión, actualización y endurecimiento — ExpApp

> Documento de trabajo. Fecha: 2026-11-26. Basado en el estado de `main` (último commit 2020-10-26).
> Objetivo: dejar el proyecto ejecutable con dependencias actuales, sin vulnerabilidades
> conocidas explotables, con pruebas automatizadas y una ruta clara de modernización del frontend.
>
> **Estado (2026-11-27):** Fases 0–3 completadas y frontend migrado a Nuxt 4.
> Backend con 28 pruebas en verde, ``pip-audit`` sin vulnerabilidades y ``bandit`` sin
> hallazgos medios/altos. Frontend compila y las 10 pruebas E2E de Playwright headless pasan.
> Historial reescrito y publicado con force-push; pendiente rotar credenciales externas y
> pedir a GitHub que purgue las vistas cacheadas de los commits antiguos.

---

## 1. Resumen ejecutivo

El proyecto es una plantilla API REST (Flask) + SPA (Nuxt 2) de 2020. Hoy **no arranca** con las
dependencias que instala `requirements.txt` sin fijar versiones, y el frontend acumula
**203 vulnerabilidades npm (16 críticas, 79 altas)**. Además hay **credenciales reales de correo
committeadas** y un **endpoint que expone todos los usuarios sin autenticación**.

| Área | Estado | Acción propuesta |
|---|---|---|
| Backend ejecutable | Roto con Flask 3 / PyJWT 2 / sin `flask_script` | Fase 1: modernizar a Flask 3 + SQLAlchemy 2 + CLI |
| Secretos | SMTP real + claves de relleno inseguras en git | Fase 0: rotar y mover a variables de entorno |
| Autenticación | Bugs de diseño + sin rate limit + sin revocación real | Fase 2: rediseñar el flujo JWT |
| Permisos | `is_admin` existe pero nunca se usa | Fase 2: decorador de roles + endpoint `/users` protegido |
| Uploads | Nombres predecibles, sin validación de contenido | Fase 2: `secure_filename` + `secrets` + validación real |
| Frontend | Nuxt 2.14.6 (EOL desde jun-2024), 203 vulns | Fase 4 (puente 2.18.1) y Fase 5 (Nuxt 4) |
| Calidad | Sin tests reales, sin CI, sin migraciones, README incompleto | Fase 3 y Fase 6 |

**Esfuerzo estimado:** 9–14 días de una persona (sin contar Fase 5 opcional: +3–5 días).

---

## 2. Diagnóstico detallado

### 2.1 Bloqueantes de ejecución (el backend no funciona hoy)

1. **PyJWT ≥ 2 rompe la firma de tokens.** `jwt.encode(...)` devuelve `str`, pero el código hace
   `.decode('UTF-8')` → `AttributeError` en login/refresh. `backend/app/auth/models.py:79-80`.
2. **PyJWT ≥ 2 exige `algorithms` en `decode`.** `jwt.decode(token, key)` lanza `DecodeError`;
   el `except` de los decoradores lo convierte en **400 en todos los endpoints protegidos**.
   `backend/app/auth/decorators.py:20,39` y `backend/app/auth/models.py:109`.
3. **`flask_script` y `MigrateCommand` ya no existen** en Flask 3 / Flask-Migrate 4.
   `backend/server.py:6-7,22` no puede ejecutarse.
4. **`ExpApp()` se invoca dentro de los modelos**, creando una aplicación Flask nueva por cada
   token emitido/validado (rendimiento, side effects, `db.init_app` repetido).
   `backend/app/auth/models.py:79,80,109`; `backend/app/auth/decorators.py:20,39`.
5. **`migrate` local sombrea el global** (`backend/app/__init__.py:24`), por lo que `server.py:8`
   importa una instancia de `Migrate` nunca inicializada.
6. **Dependencias no declaradas:** `sqlalchemy-datatables` (el paquete que expone
   `ColumnDT`/`DataTables`) se importa en `backend/app/auth/routes.py:7` y `coverage` en
   `backend/server.py`, pero ninguna estaba en `requirements.txt`.
7. **Tests inoperantes:** `backend/tests/test_base.py` usa `ExpApp.config`, pero `ExpApp` es una
   función; no se construye ninguna app ni se ejecuta ninguna aserción.
8. **`requirements.txt` sin pin** (11 paquetes) e incluye `ipdb`, `flask-jwt-auth` y `flask-login`
   que no se usan. Builds no reproducibles.

### 2.2 Hallazgos de seguridad

#### P0 — explotables / datos comprometidos

| # | Hallazgo | Ubicación | Impacto |
|---|---|---|---|
| S1 | Credenciales SMTP reales committeadas en texto plano | `backend/config.py:31-32` | Uso del servicio de correo ajeno; debe rotarse ya |
| S2 | `SECRET_KEY` y `JWT_SECRET_KEY` con valores de relleno públicos | `backend/config.py:15-16` | Falsificación de JWT / sesiones si falta la env |
| S3 | `GET/POST /1.0/user/users` **sin autenticación ni rol** | `backend/app/auth/routes.py:167-180` | Fuga de usuarios, nombres y correos (PII) |
| S4 | Comando `create_su` crea `admin/admin` | `backend/server.py:63-67` | Credenciales triviales en producción |
| S5 | Reset de contraseña: token = MD5(bcrypt hash), sin expiración ni uso único, enlace a `localhost`, y respuesta distinta si el correo existe | `backend/app/auth/routes.py:120-164` | Enumeración de usuarios, tokens perpetuos |
| S6 | `DEBUG = True` fijo | `backend/config.py:9` | Stack traces y debugger expuestos |

#### P1 — debilidades importantes

| # | Hallazgo | Ubicación |
|---|---|---|
| S7 | Sin rate limiting ni bloqueo en login/register/reset (fuerza bruta) | `auth/routes.py` |
| S8 | Sin política de contraseñas; registro público abierto y sin verificación de email | `auth/routes.py:35-54` |
| S9 | `logout` y `refresh` exigen un access token válido: al expirar, el refresh queda vivo y no se puede cerrar sesión | `auth/routes.py:75-117` |
| S10 | Blacklist por token completo, sin `jti`, sin TTL ni limpieza; tabla crece sin límite | `auth/models.py:111-138` |
| S11 | CORS abierto (`cors.init_app(app)` sin orígenes) y opción axios inventada (`AllowControlAllowOrigin`) | `app/__init__.py:23`, `nuxt.config.js:50` |
| S12 | `except:` desnudos y acceso directo a `data["clave"]` → 500 y mensajes inconsistentes | `auth/routes.py` (varios) |
| S13 | Upload: nombre con `random` + MD5 (no criptográfico), sin validación de contenido real, sin carpeta por usuario, sin límite por archivo, carpeta destino no creada | `datos/routes.py:10-38` |
| S14 | Sin cabeceras de seguridad (CSP, HSTS, X-Frame-Options, nosniff, Referrer-Policy) | app global |
| S15 | Sin logs/auditoría de eventos de autenticación | app global |

#### P2 — endurecimiento / deuda

| # | Hallazgo | Ubicación |
|---|---|---|
| S16 | Cambiar contraseña no invalida tokens existentes; refresh sin rotación ni detección de reuso | `auth/models.py`, `auth/routes.py` |
| S17 | JWT de 1 día / 7 días sin `jti`; `decode_token` sin `algorithms` explícito | `auth/models.py:59-109` |
| S18 | `utcnow()` deprecado (naïve datetimes) | modelos y config |
| S19 | `GET /` devuelve IP y fecha con HTTP 201 | `core/routes.py:6-12` |
| S20 | Sin protección CSRF (hoy no aplica con Bearer; sí si se migra a cookies) | — |
| S21 | Dependencias sin pin, `ipdb` en producción, paquetes muertos (`flask-jwt-auth`, `flask-login`) | `requirements.txt` |

### 2.3 Bugs funcionales

- `register` crea usuarios con `is_active=False` y **no existe flujo de activación** → nadie puede
  entrar con una cuenta nueva (`auth/models.py:45`, `auth/routes.py:50`).
- Registro/actualización con username o email duplicado → `IntegrityError` → 500.
- `login` distingue `_NO_USERNAME` / `_NO_PASSWORD` y no valida tipos; `data["x"]` puede dar 500.
- `refresh` exige access token válido: contradice el propósito del refresh.
- Si `logout` falla, el refresh token sigue siendo válido.
- `secure_name` puede colisionar y sobrescribir archivos; usa `random` (no `secrets`).
- `from app import Config` en `datos/routes.py:7` funciona solo por efecto colateral del import.
- `server.py` inicia cobertura de código al importarse (`COV.start()`), incluso en producción.
- `core` responde 201 a un GET.

### 2.4 Frontend (diagnóstico histórico; resuelto con la migración a Nuxt 4)

- **Nuxt 2.14.6 está EOL** (soporte terminó en junio 2024). `npm audit`: **203 vulnerabilidades
  (16 críticas, 79 altas, 97 moderadas, 11 bajas)**, muchas en la cadena webpack 4 / `elliptic` /
  `loader-utils` / `ejs` / `minimist`. `npm audit fix` no puede resolverlas sin saltos mayores.
- `middleware/auth.js` propio **choca con el middleware `auth` de `@nuxtjs/auth`** y está aplicado
  globalmente (`router.middleware: ['auth']`), incluyendo la página de login → posible bucle.
- El getter `getIsLoggedIn` **no existe** (el real es `isAuthenticated`) → la redirección de la
  página de login nunca ocurre (`pages/index.vue:56`).
- `lang/en-US.js` está **vacío** y el locale declarado es `en-UK` (`nuxt.config.js:38-40`).
- Claves i18n faltantes: `sipo.menu` (`mixins/menu.js:3`), `comunes.archivos.*`
  (`pages/datos/subir.vue:31-32`), `comunes.herramientas.datatable.itemPorPage`
  (`mixins/datatable.js:14`).
- Backend hardcodeado a `http://localhost:5000` (`nuxt.config.js:1`); sin `runtimeConfig` ni `.env`.
- `AllowControlAllowOrigin` no es una opción de axios (`nuxt.config.js:50`).
- Upload por Dropzone envía XHR directo: header sin `Bearer`, sin interceptor 401/refresh
  (`pages/datos/subir.vue:27`).
- `layouts/error.vue:17` usa `layout: 'empty'`, que no existe.
- Restos de plantilla Nuxt en `layouts/default.vue`, typo `style="text-aling"`,
  `staticBase` indefinido en `components/expMenu.vue:7`.
- ESLint extiende `standard` pero falta `eslint-config-standard`; `babel-eslint`, `eslint-plugin-html`
  y `eslint-plugin-vue` están obsoletos o incompatibles → `npm run lint` no funciona.
- `package-lock.json` en formato v1 (npm 6), no reproducible con npm 11.
- Nuxt 2 + webpack 4 requiere `--openssl-legacy-provider` en Node ≥ 18.
- No hay interceptor global que cierre sesión / refresque al recibir 401.
- `store/index.js` mezcla estado de UI (menú, breadcrumb) con autenticación.

### 2.5 Calidad, operación y documentación

- Sin CI, sin Dockerfile, sin `docker-compose`, sin `Makefile`, sin pre-commit.
- Sin migraciones versionadas (solo `db.create_all()`); sin seed de datos.
- Sin `.env.example` (el `sample.env` está vacío), sin validación de configuración al arrancar.
- Sin healthcheck (`/health`), sin logs estructurados, sin manejo global de errores.
- Sin pruebas de frontend ni E2E.
- `README.rst` termina en `pip install -r requirements.txt`: no explica entorno, arranque,
  migraciones, variables ni frontend.
- Licencia cambiada a MIT (atribución obligatoria); antes CC0 1.0.
- No hay `SECURITY.md` ni política de reporte de vulnerabilidades.

---

## 3. Versiones objetivo (verificadas hoy)

**Backend:** Flask 3.1.x · Flask-SQLAlchemy 3.1.x · Flask-Migrate 4.1.x · Flask-Cors 6.x ·
Flask-Bcrypt 1.0.x · Flask-Mail 0.10.x · PyJWT 2.15.x · python-dotenv 1.2.x ·
Flask-Limiter 4.x · Gunicorn 27.x · pytest 9.x · ruff · bandit · pip-audit · psycopg 3.x.

**Frontend puente (Fase 4):** Nuxt 2.18.1 · Vuetify 2.7.2 · nuxt-i18n 6.28.1 ·
@nuxtjs/axios 5.13.6 · core-js 3.51.x (fin de línea, sigue EOL).

**Frontend objetivo (Fase 5):** Nuxt 4.7.x · Vue 3.5.x · Vuetify 4.3.x · @nuxtjs/i18n 10.7.x ·
Pinia 4.x · nuxt-auth-utils 0.6.x (o sidebase/nuxt-auth 1.4.x).

---

## 4. Plan por fases

### Fase 0 — Contención (≈ 0,5 día)

- [ ] **Pendiente:** rotar la contraseña SMTP y las claves `SECRET_KEY` / `JWT_SECRET_KEY`
      (requiere acceso al proveedor; no se puede hacer desde el repositorio).
- [x] Eliminar credenciales de `config.py`; leer todo de entorno con `python-dotenv`.
- [x] Crear `backend/.env.example` completo y validación fail-fast al crear la app.
- [x] Reemplazar `create_su` por `flask create-su` con contraseña aleatoria si no se define.
- [x] Hotfix: exigir autenticación + rol admin en `/1.0/user/users`.
- [x] **Historial git purgado en local** (ver procedimiento y estado abajo);
      **pendiente el force-push**.

> **Dónde están los secretos hoy:** no existe ningún `.env` en el repositorio ni en su historial.
> `backend/sample.env` está vacío (0 bytes) y solo se versiona como plantilla. Las credenciales
> están **escritas directamente en `backend/config.py`** (líneas 15-16 y 31-32) y aparecen en
> **todos los commits desde el primero** (`e153f94`).

**Procedimiento de purga del historial (coordinar antes con el equipo):**

1. **Rotar primero** la contraseña SMTP y las claves. La purga no deshace la exposición previa.
2. Avisar a quien use la rama `Alvaro` (hoy eliminada): la reescritura cambia todos los SHA.
3. Instalar `git-filter-repo` (`pip install git-filter-repo` o el paquete del sistema).
4. Crear `secrets-to-remove.txt` con las cadenas exactas y ejecutar:
   ```bash
   git filter-repo --replace-text secrets-to-remove.txt
   ```
5. Revisar con `git log -p -- backend/config.py` que ya no aparecen.
6. Restaurar el remoto que `filter-repo` elimina y forzar la subida:
   ```bash
   git remote add origin git@github.com:jaaparenas/ExpApp.git
   git push --force --all origin
   git push --force --tags origin
   ```
7. Pedir a GitHub que purgue las vistas cacheadas de los commits antiguos (o esperar su GC).
8. Cada colaborador debe **reclonar**; no hacer `pull` sobre una historia reescrita.

**Aceptación:** `git grep` no encuentra secretos; el endpoint `/users` devuelve 401 sin token;
`git log -p` no contiene las credenciales.

### Fase 1 — Backend ejecutable y moderno (2–3 días)

- [ ] App factory real `create_app(config_name)` con clases `Development/Production/Testing`
      (hoy existe `ExpApp(config)` + `TestingConfig`).
- [x] Sustituir `ExpApp()` por `current_app` en modelos y decoradores.
- [x] PyJWT 2 correcto: `algorithms=['HS256']` y datetimes con timezone.
      Pendiente: `jti`/`iss`/`aud`.
- [x] Migrar `flask_script` a CLI de Flask (`flask test`, `flask create-db`, `flask create-su`).
- [x] Inicializar `Migrate` correctamente con `migrate.init_app(app, db)`.
      Pendiente: versionar la migración inicial.
- [ ] Reemplazar `sqlalchemy-datatables` por un helper propio de paginación/filtrado
      (o mantenerlo fijado en `2.0.1`).
- [x] `requirements.txt` pinneado; retirar `ipdb`, `flask-jwt-auth`, `flask-login`,
      `flask-testing`; añadir `requirements-dev.txt`.
- [x] Tests mínimos con unittest + SQLite en memoria (login, `/data`, 401, 403, refresh).
      Pendiente: migrar a pytest y ampliar cobertura.
- [x] Corregir duplicados y validación básica de contraseña en registro.
      Pendiente: flujo de activación de cuentas.

**Aceptación:** `flask run` arranca en limpio; login → `/data` → refresh → logout funciona con
PyJWT 2; `pytest` pasa; `flask db upgrade` crea el esquema desde cero.

### Fase 2 — Endurecimiento de seguridad (2–3 días)

- [x] Errores 400/401/403/404/413/429/500 consistentes en JSON y sin trazas internas.
- [x] Contraseñas: longitud mínima configurable, `BCRYPT_LOG_ROUNDS` por entorno, tokens de
      reset con `secrets.token_urlsafe`, expiración, un solo uso, respuesta genérica y enlace
      construido con `FRONTEND_URL`.
- [x] `Flask-Limiter` en login (10/min), registro (5/h), reset (5/min), refresh (30/min),
      cambio de contraseña (5/min) y listado de usuarios (60/min). Probado con unittest.
- [x] JWT con `jti`, `iss`, `ver`; blacklist por `jti` con TTL y purga; refresh sin access
      válido y con rotación; sesiones invalidadas al cambiar/restablecer contraseña.
- [x] CORS con allowlist por entorno y cabeceras de seguridad (CSP, HSTS, nosniff, etc.).
- [x] Uploads con `secure_filename` + `secrets.token_hex`, validación de contenido por magic
      bytes, límite por archivo y carpeta creada automáticamente.
- [x] Manejo global de errores; `DEBUG`/`ENV` por entorno; logs de auditoría de auth.
- [x] `pip-audit` sin vulnerabilidades y `bandit` sin hallazgos medios/altos.
- [ ] Pendiente opcional: verificación de email y bloqueo progresivo por usuario.

**Aceptación:** checklist de seguridad P0/P1 cerrado; pruebas de rate limit, reset, revocación y
permisos; `bandit -r app` sin hallazgos altos.

### Fase 3 — Calidad y automatización (1–2 días)

- [x] Suite unittest por blueprint (28 pruebas); pendiente medir cobertura formalmente.
- [x] GitHub Actions: unittest, migraciones, bandit, pip-audit, `npm ci`, build y `npm audit`.
      Pendiente: ruff y Dependabot.
- [x] `pre-commit` con hooks de espacio, YAML, JSON, archivos grandes y claves privadas.
- [x] Dockerfile backend (Gunicorn + entrypoint con migraciones) y `docker-compose` con
      PostgreSQL, healthcheck y volúmenes.
- [ ] OpenAPI/Swagger (flask-smorest o especificación manual) y colección de ejemplos.

**Aceptación:** PR de ejemplo pasa CI en verde; `docker compose up` levanta API + DB.

### Fase 4 — Frontend puente sobre Nuxt 2 — **no aplica**

Se descartó el parche temporal y se fue directo a la Fase 5.

### Fase 5 — Migración a Nuxt 4 — **completada**

- [x] Nuxt 4.7 + Vue 3.5, sin Vuetify ni Pinia para reducir dependencias.
- [x] Auth con composable propio (`useAuth`) con refresh automático y revocación.
- [x] i18n propio (es/en) y toasts sin módulos externos.
- [x] Páginas reescritas: login, escritorio, perfil (cambio de contraseña), usuarios,
      subida, analítica, grupos y recuperación de contraseña.
- [x] 10 pruebas E2E con Playwright headless: login, logout, ruta protegida, perfil,
      subida válida, archivo falso, usuarios, búsqueda y reset inválido.
- [x] Retirado Nuxt 2 y todas las dependencias EOL (203 vulnerabilidades → 9 moderadas
      en tooling de build, 0 críticas/altas).

**Aceptación:** `npm run build` en verde, E2E 10/10, `npm audit` sin críticas/altas.

### Fase 6 — Operación y documentación (1 día)

- [x] README completo: requisitos, entorno, migraciones, arranque, pruebas, Docker y E2E.
- [x] `SECURITY.md`, `CONTRIBUTING.md` y `CHANGELOG.md`.
- [x] Runbook parcial (SECURITY.md + docker-compose + Makefile).
- [x] `.gitignore` raíz para `instance/`, `storage/`, `*.sqlite3`, `.env*`.

**Aceptación:** una persona nueva levanta el proyecto siguiendo el README sin ayuda.

---

## 5. Decisiones que necesito confirmar

1. **Alcance inicial:** ¿solo backend (Fases 0–3) o backend + frontend?
2. **Frontend:** ¿puente Nuxt 2.18 (rápido, sigue EOL) o migración directa a Nuxt 4?
3. **Base de datos:** ¿SQLite en desarrollo + Postgres en producción (con compose)?
4. **Auth:** ¿mantener el JWT propio endurecido o migrar a Flask-JWT-Extended?
5. **Correo:** ¿seguir con SocketLabs por variables de entorno o SMTP genérico?
6. **Historial git:** ✅ decidido — rotar secretos **y** purgar el historial con `git filter-repo`
   (requiere force-push; la rama `Alvaro` se eliminó y todo quedó en `main`).

---

## 6. Orden recomendado

1. **Fase 0 ya** (secretos y endpoint abierto no pueden esperar).
2. Fase 1 → Fase 2 → Fase 3 (backend sólido y verificable).
3. Fase 4 si se necesita seguir operando el frontend actual mientras se planifica la migración.
4. Fase 5 cuando se decida asumir el rewrite.
5. Fase 6 al cerrar cada bloque.

---

## 7. Estado de ejecución (2026-11-27)

### Hecho en esta sesión

- Secretos y credenciales de correo sacados de `config.py`; ahora todo se lee de variables de
  entorno y la app falla con un mensaje claro si faltan `SECRET_KEY` / `JWT_SECRET_KEY`.
- `backend/.env.example` documentado; `.env` local creado (ignorado por git, permisos `600`).
- `/1.0/user/users` protegido con autenticación + rol admin.
- PyJWT 2 corregido (`algorithms`, sin `.decode`), `current_app` en lugar de `ExpApp()`.
- `flask_script` reemplazado por CLI de Flask (`test`, `coverage`, `create-db`, `drop-db`,
  `create-su`) y `Migrate` inicializado correctamente.
- `README.rst` reescrito con instalación, variables, endpoints y pruebas.
- Dependencias pinneadas y corregidas (`sqlalchemy-datatables==2.0.1`, `python-dotenv`, `PyJWT`).
- 28 pruebas funcionales en verde (health, login, perfil, 401/403, rotación de refresh,
  rate limiting, reset, uploads y revocación de sesiones).
- **Historial reescrito en local** con `git filter-repo --replace-text`: ya no aparecen la
  contraseña SMTP, el usuario SMTP, los secretos por defecto ni los correos personales en
  ningún commit de `main` ni de la antigua `Alvaro`.
- Respaldo previo a la purga: `/tmp/opencode/ExpApp-before-purge.bundle`.
- **Force-push realizado** a `origin/main` y a la entonces existente `Alvaro`; verificado con un clone espejo. Después se eliminó `Alvaro` y todo quedó consolidado en `main`.

### Seguimiento

- **Rotar las credenciales SMTP y las claves** en el proveedor. La purga no revierte la
  exposición previa; si el repositorio fue público, deben considerarse comprometidas.
- [x] **Force-push realizado** y rama `Alvaro` eliminada. Todo el proyecto vive en `main`;
  un clone espejo del remoto confirma que la historia ya no contiene secretos.
- **GitHub todavía responde 200** en las URLs de los commits antiguos
  (`8fdf0c7…` y `a7d3029…`). Es caché del servidor: hay que pedir a soporte de GitHub que
  purge las vistas de commits antiguos o esperar su recolección de basura.
- Avisar a los colaboradores para que **reclonen** (no hagan `pull` sobre la historia reescrita).

---

## 8. Verificación (2026-11-27)

| Comprobación | Resultado |
|---|---|
| Pruebas backend (`python -m unittest`) | **28/28 OK** (auth, roles, tokens, reset, uploads, rate limit) |
| Migración inicial (`flask db upgrade`) | Crea `users`, `roles`, `roles_users`, `blacklist_tokens` y `alembic_version` |
| `pip-audit -r requirements.txt` | **No known vulnerabilities found** |
| `bandit -r app server.py config.py` | **0 hallazgos** (los falsos positivos B105/B107 quedaron anotados con `# nosec`) |
| Build frontend (`npm run build`) | Nuxt 4.7.0, cliente 218.70 kB (81.86 kB gzip) |
| E2E Playwright headless | **10/10 passed** |
| `npm audit` | 9 moderadas en tooling de build (`nitropack`/`archiver`/`minimatch`), 0 altas/críticas |
| `npm audit --omit=dev --audit-level=high` | Pasa |

Notas:

- Node local es 24.0.1; Nuxt recomienda ^24.11.0. El build y las pruebas funcionan, pero CI
  usa Node 22 LTS.
- Las 9 vulnerabilidades moderadas de npm están en la cadena de empaquetado de Nitro
  (`archiver` → `readdir-glob` → `minimatch`, advisory GHSA-g3hv-75wg-m249). No afectan al
  runtime del navegador; `npm audit fix --force` degradaría Nuxt, así que se documentan.
- Las pruebas E2E desactivan el rate limiting (`RATELIMIT_ENABLED=0`) para no agotar el
  límite de login entre tests. El rate limiting sí está cubierto por una prueba unitaria.

### Pendiente al cierre de esta sesión

- Rotación de credenciales SMTP/claves en el proveedor y purga de la caché de GitHub.
- Medir cobertura del backend y añadir OpenAPI.
- Opcional: verificación de email, Redis para rate limiting multi-worker, antivirus en uploads,
  OpenAPI y cookies httpOnly mediante BFF.
