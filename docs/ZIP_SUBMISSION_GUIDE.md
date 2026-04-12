# ZIP Submission Guide — What to Include and Exclude

Use this guide **before** creating the ZIP file for your instructor. It explains what is **mandatory**, what is **optional**, and what should **not** be included. **No deletions are performed here** — this is guidance only.

---

## 1. Do NOT Include (Exclude from ZIP)

These should **not** be in the submission** either by deleting them before zipping or by excluding them when creating the ZIP.

### 1.1 Must Exclude — Security & Local Environment

| Item | Location | Reason |
|------|----------|--------|
| **`.env`** | Project root | Contains secrets (e.g. MongoDB URI, JWT secret). Never share with others. Instructor will use their own environment. |
| **`*.env`** (any `.env` file) | Anywhere | Same as above. |

### 1.2 Must Exclude — Regeneratable / Machine-Specific

| Item | Location | Reason |
|------|----------|--------|
| **`node_modules`** | `frontend/node_modules/` | Dependencies; very large (~thousands of files). Instructor runs `npm install` from `frontend/` to get them. |
| **`__pycache__`** | `backend/` (and any subfolder) | Python bytecode cache. Regenerated when running the app. Not source code. |
| **`.pyc` files** | `backend/` | Same as above. |
| **Virtual environment** | e.g. `venv/`, `env/`, `.venv/` | Python virtual env; instructor creates their own and runs `pip install -r requirements.txt`. |
| **`dist`** (or `build`) | `frontend/dist/` or `frontend/build/` | Built frontend output. Instructor runs `npm run build` if needed. |

### 1.3 Should Exclude — IDE / Editor / OS

| Item | Location | Reason |
|------|----------|--------|
| **`.idea`** | Project root (JetBrains) | IDE settings; not part of the project. |
| **`.vscode`** | Project root | Editor settings; optional to share. Exclude if it has machine-specific paths or secrets. |
| **`.cursor`** | Project root | Cursor IDE; not needed for grading. |
| **`Thumbs.db`** | Any (Windows) | OS thumbnail cache. |
| **`.DS_Store`** | Any (macOS) | OS folder settings. |

### 1.4 Optional to Exclude

| Item | Location | Reason |
|------|----------|--------|
| **`.git`** | Project root | Version history. Include only if instructor asked for Git history; otherwise excluding keeps ZIP smaller. |

---

## 2. Not Required for Submission (Optional to Include)

Including them does not hurt; excluding them keeps the ZIP smaller. Your choice.

| Item | Location | Note |
|------|----------|------|
| **Root `package-lock.json`** | Project root | Minimal lockfile; not used for frontend. Can exclude. |
| **`docker-compose.yml`** / **`docker-compose.dev.yml`** | Project root | Useful if instructor runs with Docker; include if you want to show deployment. |
| **`backend/Dockerfile`**, **`frontend/Dockerfile`** | backend/, frontend/ | Same as above. |
| **`backend/.dockerignore`** | backend/ | Used by Docker build; include if you include Dockerfiles. |
| **`frontend/nginx.conf`** | frontend/ (if present) | Used when serving frontend in Docker; include if you include Docker setup. |

---

## 3. Mandatory to Include (Required for Submission)

The instructor must be able to run the project and understand it. Include everything below.

### 3.1 Project Root

| File / Folder | Purpose |
|---------------|--------|
| **`README.md`** | Setup instructions, how to run backend/frontend, seed script. **Essential.** |
| **`.env.example`** (if you have one) | Template for env vars (no real secrets). If you don’t have it, consider adding one so instructor knows what variables to set (e.g. `MONGODB_URI`, `MONGODB_DB`). |

### 3.2 Backend (`backend/`)

| File / Folder | Purpose |
|---------------|--------|
| **`run.py`** | Application entry point. |
| **`requirements.txt`** | Python dependencies; needed for `pip install -r requirements.txt`. |
| **`seed_assessment.py`** | Seeds assessment questions; instructor must run this once. |
| **`app/`** (entire folder) | All application code: `__init__.py`, `config.py`, `extensions.py`, `api/`, `services/`, `utils/`. |
| **`Dockerfile`** | Optional but good if you use Docker. |
| **`.dockerignore`** | Optional; use if you include Dockerfile. |

Do **not** include: `__pycache__/`, `.pyc`, `venv/` (or any virtualenv), `.env`.

### 3.3 Frontend (`frontend/`)

| File / Folder | Purpose |
|---------------|--------|
| **`package.json`** | Dependencies and scripts; needed for `npm install` and `npm run dev`. |
| **`package-lock.json`** | Locked dependency versions; recommended so instructor gets same versions. |
| **`index.html`** | HTML entry. |
| **`vite.config.js`** | Vite config (dev server, proxy). |
| **`tailwind.config.js`** | Tailwind theme/config. |
| **`postcss.config.js`** | PostCSS (Tailwind). |
| **`src/`** (entire folder) | All source: `main.jsx`, `App.jsx`, `index.css`, `api/`, `components/`, `context/`, `pages/`. |
| **`Dockerfile`**, **`nginx.conf`** | Optional; include if you want instructor to run via Docker. |

Do **not** include: `node_modules/`, `dist/` (or `build/`).

### 3.4 Documentation (`docs/`)

| File | Purpose |
|------|--------|
| **`STRATEGY_DOCUMENT.md`** | Overall strategy and requirements; good for grading. |
| **`PROTOTYPE_VIDEO_PRESENTATION_SCRIPT.md`** | Script for your prototype video; shows understanding. |
| **`QA_AUDIT_PROTOTYPE_FR1_FR2.md`** | If you have it; shows quality/audit. |
| **`ZIP_SUBMISSION_GUIDE.md`** | This file; optional to include in ZIP. |

---

## 4. Summary Checklist

Before creating the ZIP:

- [ ] **Exclude** `frontend/node_modules/`
- [ ] **Exclude** any `__pycache__/` and `.pyc` under `backend/`
- [ ] **Exclude** `.env` (and any file with real secrets)
- [ ] **Exclude** virtual environment folder (`venv/`, `env/`, etc.) if present
- [ ] **Exclude** `frontend/dist/` (or `build/`) if present
- [ ] **Exclude** `.git/` unless required
- [ ] **Include** `README.md`, `backend/` (without cache/venv), `frontend/` (without node_modules/dist), `docs/` (as needed)
- [ ] **Include** `backend/requirements.txt`, `frontend/package.json` (and preferably `package-lock.json`)
- [ ] **Include** all source under `backend/app/` and `frontend/src/`

---

## 5. How to Create the ZIP (Without Deleting Anything)

You can create the ZIP **without deleting** anything from your project by **selecting only the right folders/files** when zipping:

1. **Option A — Exclude when zipping**  
   When creating the ZIP (e.g. right‑click → “Compress” or “Send to → Compressed folder”), add only:
   - Root: `README.md`, (optional: `.env.example`), (optional: `docker-compose.yml`, `docker-compose.dev.yml`, root `package-lock.json` if you want)
   - Folder: `backend/` — but **exclude** inside it: `__pycache__`, `*.pyc`, `venv/` (or your venv name)
   - Folder: `frontend/` — but **exclude** inside it: `node_modules/`, `dist/`
   - Folder: `docs/`
   - Do **not** add: `.env`, `.git` (unless required)

2. **Option B — Copy to a clean folder, then zip**  
   - Create a new folder (e.g. `ProjectSubmission`).
   - Copy into it: `README.md`, `backend/`, `frontend/`, `docs/`, and any root files you want (e.g. `docker-compose.yml`).
   - From the copied `backend/`, delete (only in the copy): `__pycache__`, `venv/`, `.env` if it was copied.
   - From the copied `frontend/`, delete (only in the copy): `node_modules/`, `dist/`.
   - Do **not** copy `.env` from the original project.
   - Zip the `ProjectSubmission` folder.

---

## 6. After Submission — What Instructor Will Do

Your instructor will typically:

1. Unzip the project.
2. Create their own `.env` (e.g. from `.env.example`) with their MongoDB URI and DB name.
3. Run: `cd backend && pip install -r requirements.txt && python seed_assessment.py && python run.py`.
4. Run: `cd frontend && npm install && npm run dev`.
5. Open the app in the browser and test FR1 (register, login, logout) and FR2 (assessment, result).

If you exclude `node_modules`, `__pycache__`, `.env`, and virtualenv, and include all source and config files above, the submission will be complete and runnable without sharing secrets or unnecessary files.
