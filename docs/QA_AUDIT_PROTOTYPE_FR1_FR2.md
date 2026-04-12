# QA Audit: Prototype Phase — FR1 & FR2 Only

**Audit Date:** 2026  
**Scope:** Verify prototype contains ONLY FR1 (User Registration & Authentication) and FR2 (Skill Assessment & Domain Recommendation).

---

## 1) CHECKLIST: FR1 & FR2 → EXACT CODE LOCATIONS

### FR1: User Registration and Authentication

| Requirement                                                  | Evidence                                              | File Path                                    | Function/Class/Route                                                                                                                                                                                   |
| ------------------------------------------------------------ | ----------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Role-based registration (Student, Mentor, Administrator)** | Backend accepts `role`, validates against ROLES tuple | `backend/app/services/auth_service.py`       | `ROLES = ('Student', 'Mentor', 'Administrator')` (line 7); `create_user()` (lines 36–58) checks `if role not in ROLES`                                                                                 |
|                                                              | Frontend role selection                               | `frontend/src/pages/Register.jsx`            | `ROLES = ['Student', 'Mentor', 'Administrator']` (line 8); `<select value={role}>` (lines 56–60)                                                                                                       |
|                                                              | API endpoint                                          | `backend/app/api/auth.py`                    | `RegisterView.post()` (lines 21–40); route: **POST /api/auth/register**                                                                                                                                |
| **Login**                                                    | Backend                                               | `backend/app/api/auth.py`                    | `LoginView.post()` (lines 46–62); **POST /api/auth/login**                                                                                                                                             |
|                                                              | Frontend                                              | `frontend/src/pages/Login.jsx`               | `handleSubmit` calls `login(email, password)` (lines 24–26); `frontend/src/context/AuthContext.jsx` `login()` (lines 25–31) calls `authApi.login()`                                                    |
| **Logout**                                                   | Backend                                               | `backend/app/api/auth.py`                    | `LogoutView.post()` (lines 65–71); **POST /api/auth/logout**                                                                                                                                           |
|                                                              | Frontend                                              | `frontend/src/context/AuthContext.jsx`       | `logout()` (lines 33–39) calls `authApi.logout()`, clears `localStorage`; `frontend/src/components/layout/DashboardLayout.jsx` `handleLogout` (lines 22–25) calls `logout()` then `navigate('/login')` |
| **Password validation/check**                                | Server-side strength (register)                       | `backend/app/services/auth_service.py`       | `validate_password()` (lines 20–33): min 8 chars, 1 upper, 1 lower, 1 digit                                                                                                                            |
|                                                              | Server-side check (login)                             | `backend/app/services/auth_service.py`       | `authenticate_user()` (lines 62–73) uses `check_password()` (lines 15–17); `hash_password()` bcrypt (lines 10–12)                                                                                      |
|                                                              | API uses validation                                   | `backend/app/api/auth.py`                    | `RegisterView.post()` calls `validate_password(password)` (lines 33–35)                                                                                                                                |
|                                                              | Client-side (register)                                | `frontend/src/pages/Register.jsx`            | `password !== confirmPassword` (line 23); `password.length < 8` (line 27)                                                                                                                              |
| **Role-based access control**                                | Backend RBAC                                          | `backend/app/utils/decorators.py`            | `role_required(*allowed_roles)` (lines 8–21); `verify_jwt_in_request()`, then check `user.get('role') in allowed_roles`                                                                                |
|                                                              | Assessment endpoints Student-only                     | `backend/app/api/assessment.py`              | `@role_required('Student')` on `QuestionsView.get` (line 18), `SubmitView.post` (line 28), `ResultView.get` (line 47)                                                                                  |
|                                                              | Frontend route protection                             | `frontend/src/components/ProtectedRoute.jsx` | `roles && !roles.includes(user.role)` → redirect to `/dashboard` (lines 22–24)                                                                                                                         |
|                                                              | Frontend routes                                       | `frontend/src/App.jsx`                       | `/assessment` and `/result` wrapped in `<ProtectedRoute roles={['Student']}>` (lines 28, 36)                                                                                                           |
| **Session handling**                                         | JWT issue & storage                                   | `backend/app/api/auth.py`                    | `create_access_token(identity=user['id'])` (line 58); `backend/app/config.py` `JWT_ACCESS_TOKEN_EXPIRES`, `JWT_TOKEN_LOCATION = ['headers']`                                                           |
|                                                              | Client session                                        | `frontend/src/context/AuthContext.jsx`       | On login: `localStorage.setItem('access_token', …)`, `localStorage.setItem('user', …)` (lines 27–28); on load: read from localStorage (lines 11–19)                                                    |
|                                                              | Token sent on requests                                | `frontend/src/api/client.js`                 | Request interceptor: `Authorization: Bearer ${token}` (lines 12–17)                                                                                                                                    |
|                                                              | 401 → clear session                                   | `frontend/src/api/client.js`                 | Response interceptor: on 401 clear token/user and redirect to `/login` (lines 21–28)                                                                                                                   |

**FR1 route summary**

- **POST /api/auth/register** — RegisterView
- **POST /api/auth/login** — LoginView
- **POST /api/auth/logout** — LogoutView

**Frontend routes:** `/login`, `/register`, `/dashboard` (any authenticated), `/assessment` (Student), `/result` (Student).

---

### FR2: Skill Assessment and Domain Recommendation

| Requirement                                                      | Evidence                | File Path                                    | Function/Class/Route                                                                                                                                                                             |
| ---------------------------------------------------------------- | ----------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Online MCQ assessment (DigiSkills domains)**                   | Question bank & domains | `backend/seed_assessment.py`                 | `QUESTIONS` list with `domain`: Graphic Design, Content Writing, Programming, Freelancing, E-Commerce, QuickBooks, AutoCAD (lines 51–184)                                                        |
|                                                                  | Domain constant         | `backend/app/services/assessment_service.py` | `DOMAINS = ['Graphic Design', 'Content Writing', 'Programming', 'Freelancing', 'E-Commerce', 'QuickBooks', 'AutoCAD']` (lines 8–15)                                                              |
|                                                                  | Get questions API       | `backend/app/api/assessment.py`              | `QuestionsView.get()` (lines 17–21); **GET /api/assessment/questions**                                                                                                                           |
|                                                                  | Get questions service   | `backend/app/services/assessment_service.py` | `get_questions()` (lines 18–25); strips `correct_answer` before sending                                                                                                                          |
|                                                                  | Frontend MCQ UI         | `frontend/src/pages/Assessment.jsx`          | Fetches `assessmentApi.getQuestions()` (lines 28–32); renders `q?.options` as buttons (lines 82–87); `q?.domain` shown as Badge (lines 77–78)                                                    |
| **Automated score calculation**                                  | Backend scoring         | `backend/app/services/assessment_service.py` | `submit_assessment()` (lines 28–101): compares `selected == q.get('correct_answer')`, aggregates per domain, `overall_score = round(100 * total_correct / total_questions)` (line 73)            |
|                                                                  | API                     | `backend/app/api/assessment.py`              | `SubmitView.post()` (lines 27–39); **POST /api/assessment/submit** with body `{ answers }`                                                                                                       |
| **Display recommended freelancing domains based on performance** | Recommendation logic    | `backend/app/services/assessment_service.py` | `domain_scores.sort(key=lambda x: x['score'], reverse=True)`; `recommended_domain = domain_scores[0]['domain']`; `recommended_domains = [d['domain'] for d in domain_scores[:3]]` (lines 68–71)  |
|                                                                  | Stored & returned       | `backend/app/services/assessment_service.py` | Stored in `assessment_doc` (lines 81–92); return dict includes `recommended_domain`, `recommended_domains`, `domain_scores`, `overall_score` (lines 94–101)                                      |
|                                                                  | Get result API          | `backend/app/api/assessment.py`              | `ResultView.get()` (lines 45–53); **GET /api/assessment/result**                                                                                                                                 |
|                                                                  | Get result service      | `backend/app/services/assessment_service.py` | `get_latest_result()` (lines 105–116)                                                                                                                                                            |
|                                                                  | Frontend display        | `frontend/src/pages/Result.jsx`              | `result.recommended_domain` / `result.recommended_domains?.[0]` (lines 45–46); `result-highlight__domain`: "Recommended Domain: {recommended}" (line 52); table of `domain_scores` (lines 62–70) |

**FR2 route summary**

- **GET /api/assessment/questions** — QuestionsView (Student only)
- **POST /api/assessment/submit** — SubmitView (Student only)
- **GET /api/assessment/result** — ResultView (Student only)

---

## 2) MISSING ITEMS & EXTRA FEATURES

### Missing (none identified)

- All FR1 and FR2 bullets above have a direct implementation and location.

### Extra (beyond FR1/FR2)

| Item                          | Location                                                                                      | Notes                                                                                                                                                                                                            |
| ----------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GET /api/auth/profile**     | `backend/app/api/auth.py`: `ProfileView.get()` (lines 75–84); route **GET /api/auth/profile** | Not required by FR1. Supports “current user” from token; session is already handled by JWT + localStorage. Frontend does **not** call `authApi.profile()` (AuthContext uses login response + localStorage only). |
| **authApi.profile** in client | `frontend/src/api/client.js`: `profile: () => client.get('/auth/profile')` (line 37)          | Exposed but unused; could be removed for strict prototype scope.                                                                                                                                                 |

**Verdict:** One extra backend endpoint (profile) and one unused frontend API method. No other FR3–FR10 features (no tasks, submissions, mentor dashboard, portfolio, chatbot, admin panel, workspace, payment) are present.

---

## 3) RUNNING THE PROJECT & CONFIRMING FLOWS

### Prerequisites

- MongoDB running on `localhost:27017` (or set `MONGODB_URI` / `MONGODB_DB` in `.env`).
- Python 3.10+ and Node 18+.

### Commands

```bash
# 1) Seed assessment questions (once)
cd backend
pip install -r requirements.txt
python seed_assessment.py

# Expected: "Using MONGODB_URI: ..." and "Inserted 21 assessment questions."

# 2) Start backend
python run.py

# Expected: "WARNING: This is a development server." and serving on http://0.0.0.0:5000

# 3) In another terminal — start frontend
cd frontend
npm install
npm run dev

# Expected: "Local: http://localhost:5173/"
```

### Flow 1: Register → Login → RBAC → Logout

1. **Register**
   - Open http://localhost:5173/register
   - Enter email, name (optional), select role **Student** (or Mentor/Administrator), password (e.g. `Test1234`), confirm password → Submit
   - **Expected:** 201 from POST /api/auth/register; then login called; redirect to /dashboard

2. **Login**
   - Open http://localhost:5173/login
   - Enter same email and password → Sign In
   - **Expected:** 200 from POST /api/auth/login with `access_token` and `user`; redirect to /dashboard

3. **RBAC**
   - As **Student:** Visit /dashboard (OK), /assessment (OK), /result (OK)
   - As **Mentor** or **Administrator:** Visit /dashboard (OK); visit /assessment or /result → **Expected:** redirect to /dashboard (403 from API if called directly; frontend ProtectedRoute redirects)

4. **Logout**
   - Click Log out in sidebar (or wherever `handleLogout` is wired)
   - **Expected:** POST /api/auth/logout (200); localStorage cleared; redirect to /login

### Flow 2: Assessment → Score → Recommendation

1. **Start assessment**
   - As Student, go to Dashboard → Start Assessment (or /assessment)
   - **Expected:** GET /api/assessment/questions returns 21 items; page shows MCQ by domain (e.g. Graphic Design)

2. **Submit**
   - Answer all questions, click Submit
   - **Expected:** POST /api/assessment/submit with `answers` array; response has `result.overall_score`, `result.recommended_domain`, `result.domain_scores`

3. **Result**
   - **Expected:** Redirect to /result; GET /api/assessment/result returns latest; page shows “Recommended Domain: {name}”, “Overall Score: X%”, and table of scores by domain

### Optional: API checks (no UI)

```bash
# Register
curl -s -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d "{\"email\":\"test@test.com\",\"password\":\"Test1234\",\"role\":\"Student\",\"name\":\"Test\"}"

# Login (use token in next calls)
curl -s -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@test.com\",\"password\":\"Test1234\"}"

# Questions (replace TOKEN)
curl -s http://localhost:5000/api/assessment/questions -H "Authorization: Bearer TOKEN"
```

---

## 4) EVIDENCE SUMMARY

| Step | Command/Action              | Expected output / behaviour                                   |
| ---- | --------------------------- | ------------------------------------------------------------- |
| 1    | `python seed_assessment.py` | "Using MONGODB_URI: ...", "Inserted 21 assessment questions." |
| 2    | `python run.py`             | Flask dev server on port 5000                                 |
| 3    | `npm run dev`               | Vite dev server on port 5173                                  |
| 4    | Register (Student)          | 201, then redirect to dashboard                               |
| 5    | Login                       | 200 + token; redirect to dashboard                            |
| 6    | Student opens /assessment   | 200 questions; MCQ UI                                         |
| 7    | Submit assessment           | 200 + result; redirect to /result                             |
| 8    | /result page                | Recommended domain + overall score + table                    |
| 9    | Mentor opens /assessment    | Redirect to /dashboard (RBAC)                                 |
| 10   | Logout                      | 200; redirect to /login; token cleared                        |

**Screenshots / manual checks (for human auditor):**

1. **Register:** Form with role dropdown (Student, Mentor, Administrator) and password/confirm.
2. **Login:** Email + password; after submit, dashboard with greeting.
3. **Dashboard (Student):** “Start Assessment” and “View Last Result” visible.
4. **Assessment:** One question per view, domain badge, options as buttons, Previous/Next/Submit.
5. **Result:** “Recommended Domain: X”, “Overall Score: Y%”, and “Scores by Domain” table.

---

## 5) GAPS & MINIMAL FIXES

**No functional gaps:** FR1 and FR2 are implemented and traceable to the locations above.

**Optional (strict prototype-only):**

- **Remove or keep GET /api/auth/profile**
  - To restrict to FR1 only: remove the profile route and the `ProfileView` registration so the API exposes only register, login, logout.
  - Minimal patch (optional):

```python
# backend/app/api/auth.py — REMOVE profile route and view class if excluding profile
# Delete lines 75-84 (ProfileView class) and line 94 (auth_bp.add_url_rule('/profile', ...))
```

- **Remove unused `authApi.profile`** (optional):

```javascript
// frontend/src/api/client.js — remove from authApi object:
// delete the line:  profile: () => client.get('/auth/profile'),
```

**Conclusion:** The prototype implements only FR1 and FR2. The only non-required additions are the profile endpoint and the unused profile API method; they do not affect the audit criteria.
