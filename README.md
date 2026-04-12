# AI-Supported Virtual Internship Hub (Prototype)

Prototype implementing **FR1: User Registration & Authentication** and **FR2: Skill Assessment & Domain Recommendation**.

## Prerequisites

- **MongoDB** (local or Docker)
- **Python 3.10+**
- **Node.js 18+**

## Quick Start (Local Development)

### 1. Start MongoDB

Using Docker:

```bash
docker run -d -p 27017:27017 --name mongodb mongo:7
```

Or install MongoDB locally and ensure it runs on `localhost:27017`.

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python seed_assessment.py   # Seed assessment questions (run once)
python run.py              # Start API on http://localhost:5000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                # Start on http://localhost:5173
```

### 4. Seed Assessment Questions

Before taking the assessment, run:

```bash
cd backend
python seed_assessment.py
```

**FR3 — Tasks:** seed sample tasks (run once):

```bash
cd backend
python seed_tasks.py
```

## Usage

1. **Register** at http://localhost:5173/register (choose role: Student, Mentor, or Administrator)
2. **Login** at http://localhost:5173/login
3. **Students**: Go to Dashboard → Start Assessment → Complete MCQs → View Result
4. **Mentor/Administrator**: Placeholder dashboards (full features in final phase)

## API Endpoints

| Method | Endpoint                  | Description                            |
| ------ | ------------------------- | -------------------------------------- |
| POST   | /api/auth/register        | Register (email, password, role, name) |
| POST   | /api/auth/login           | Login (email, password)                |
| POST   | /api/auth/logout          | Logout (requires token)                |
| GET    | /api/assessment/questions | Get MCQ questions (Student only)       |
| POST   | /api/assessment/submit    | Submit answers (Student only)          |
| GET    | /api/assessment/result    | Get latest result (Student only)       |
<<<<<<< HEAD
| POST   | /api/submissions/writing  | Submit writing text (`assignment_id`, `text_content`) — Student; runs evaluation |
| POST   | /api/submissions/programming | Submit Python code (`assignment_id`, `code_content`) — Student; runs test cases |
| GET    | /api/submissions/&lt;id&gt; | Get submission (own) with evaluation   |
| GET    | `/api/submissions/assignment/<assignment_id>/latest` | Latest submission for an assignment |

**Writing evaluation (automated):** grammar-style heuristics, word count vs task `min_words`/`max_words`, keyword relevance, similarity vs optional `reference_text`. Task `task_type: "writing"`.

**Programming evaluation (Python):** runs `solution.py` per test with `stdin` / compares stdout to `expected_stdout`. Task `task_type: "programming"`, `language: "python"`, optional `test_cases` array and `timeout_seconds`.

**Seed tasks:** `python seed_writing_task.py` / `python seed_programming_task.py` (optional: `STUDENT_EMAIL` in `.env`).
=======
| GET    | /api/tasks/recommended    | Ranked tasks + reasons; saves snapshot (Student) |
| GET    | /api/tasks                | Browse open tasks (`domain`, `difficulty`, `page`, `limit`) |
| GET    | /api/tasks/assignments/me | Current student assignments              |
| GET    | `/api/tasks/<id>`         | Task detail (Student)                  |
| POST   | `/api/tasks/<id>/claim`    | Start task; stores recommendation snapshot |
>>>>>>> origin/master

## Docker (Full Stack)

```bash
# Build and run
docker-compose up -d

# Seed questions (run backend once)
docker-compose exec backend python seed_assessment.py

# Access: http://localhost:5173 (or port 80 if using nginx)
```

## Project Structure

```
├── backend/           # Flask API
│   ├── app/
<<<<<<< HEAD
│   │   ├── api/       # Auth, Assessment, Submissions
=======
│   │   ├── api/       # Auth, Assessment, Tasks (FR3)
>>>>>>> origin/master
│   │   ├── services/  # Business logic
│   │   └── utils/     # RBAC decorators
│   ├── run.py
│   ├── seed_assessment.py
<<<<<<< HEAD
│   ├── seed_writing_task.py
│   ├── seed_programming_task.py
=======
│   ├── seed_tasks.py
>>>>>>> origin/master
│   └── requirements.txt
├── frontend/          # React + Vite
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── context/   # Auth context
│   │   ├── pages/     # Login, Register, Dashboard, Assessment, Result
│   │   └── components/
│   └── package.json
└── docs/              # Strategy document
```

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Assessment Domains

Graphic Design, Content Writing, Programming, Freelancing, E-Commerce, QuickBooks, AutoCAD (aligned with DigiSkills courses).
