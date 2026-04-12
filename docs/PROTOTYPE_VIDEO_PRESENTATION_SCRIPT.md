# Prototype Video Presentation Script

## AI-Supported Virtual Internship Hub — FR1 & FR2

**Target length: ~10 minutes**

---

## How to Use This Document

- **Sections 1–4**: Explanation and talking points (what to say in the video).
- **Section 5**: File-by-file responsibility (reference while explaining or showing code).
- **Section 6**: Logic of major functions (for deep understanding and Q&A).
- **Section 7**: Suggested demo flow and timing.

Read the whole document once before recording. You can present by following the script or using it as bullet points.

---

# PART 1 — INTRODUCTION (About 1 minute)

**[Say:]**

"Hello. This video presents the prototype for the AI-Supported Virtual Internship Hub. The prototype implements two functional requirements: **FR1 — User Registration and Authentication**, and **FR2 — Skill Assessment and Domain Recommendation**. I will explain how each was implemented in simple terms, then show the working prototype."

---

# PART 2 — FR1: USER REGISTRATION AND AUTHENTICATION (About 2.5 minutes)

## 2.1 What FR1 Is (In Simple Words)

**FR1** is the part of the system that:

1. **Lets users create an account** — They choose a role (Student, Mentor, or Administrator), enter email and password, and the system saves them safely.
2. **Lets users sign in and sign out** — After login, the system remembers who they are for the rest of the session.
3. **Checks passwords** — Passwords must be strong (length, uppercase, lowercase, digit).
4. **Controls who can do what** — For example, only Students can take the assessment; Mentors and Admins have different access (enforced in the backend).
5. **Keeps the session** — The frontend stores a token; every request to the backend sends this token so the server knows the user.

So FR1 = **registration + login/logout + password rules + role-based access + session (token) handling**.

## 2.2 Main Ideas Behind FR1

- **Roles**: Exactly three — Student, Mentor, Administrator. Stored in the database with each user.
- **Security**: Passwords are never stored as plain text. They are hashed with **bcrypt**; only the hash is saved. On login we compare the entered password with the hash.
- **Session**: We use **JWT (JSON Web Token)**. When the user logs in, the server returns an access token. The browser sends this token in the header of every request. The server checks the token to know “who is this user?” and “what role do they have?”.
- **Role-based access**: Some API routes (e.g. assessment) are protected so that only users with role **Student** can call them. This is done with a decorator that checks the JWT and then the user’s role.

## 2.3 What You Can Say in the Video

"FR1 handles registration and login. Users register with email, password, and a role — Student, Mentor, or Administrator. Passwords are validated for strength and then hashed with bcrypt before storing. Login returns a JWT token; the frontend keeps this token and sends it with every request. The backend uses this token and the user’s role to decide who can access which features — for example, only Students can take the assessment. So FR1 gives us role-based registration, login and logout, password validation, role-based access control, and session handling via JWT."

---

# PART 3 — FR2: SKILL ASSESSMENT AND DOMAIN RECOMMENDATION (About 2.5 minutes)

## 3.1 What FR2 Is (In Simple Words)

**FR2** is the part that:

1. **Shows an online MCQ test** — Questions are stored in the database. Each question belongs to a **domain** (e.g. Graphic Design, Content Writing, Programming).
2. **Calculates scores automatically** — When the student submits answers, the backend compares each answer to the correct one, counts correct answers per domain and overall, and computes percentages.
3. **Recommends freelancing domains** — Based on scores, the system picks the best-performing domain (and top 3) as the “recommended domain(s)” and shows them on the result screen.

So FR2 = **online MCQs + automatic scoring + recommended domains based on performance**.

## 3.2 Assessment Areas (DigiSkills-Aligned)

The domains we use are: **Graphic Design, Content Writing, Programming, Freelancing, E-Commerce, QuickBooks, AutoCAD** (and “Other” if needed). These match the DigiSkills-style areas mentioned in the requirement.

## 3.3 Main Ideas Behind FR2

- **Questions**: Stored in MongoDB collection `assessment_questions`. Each question has: question text, options, correct answer index, and **domain**.
- **No cheating**: The correct answer is **never** sent to the frontend. Only question text and options are sent; the backend does all scoring.
- **Scoring**: For each submitted answer we check if the selected option index matches the stored correct index. We count correct per domain and in total, then compute percentage per domain and overall.
- **Recommendation**: Domains are sorted by score (highest first). The top domain is the main recommendation; we also store and can show the top three.

## 3.4 What You Can Say in the Video

"FR2 is the skill assessment and domain recommendation module. Students see an online MCQ test. Questions are grouped by domains like Graphic Design, Content Writing, Programming, Freelancing, E-Commerce, QuickBooks, and AutoCAD. When the student submits, the backend calculates how many answers were correct in each domain and overall, then recommends the best-performing domain — and the top three — based on that performance. So we have online MCQs, automated score calculation, and display of recommended freelancing domains, as required."

---

# PART 4 — DATA FLOW (STEP BY STEP) (About 2 minutes)

## 4.1 Registration Flow

1. User fills the form (email, password, name, role) on the **Register** page.
2. Frontend sends a **POST** request to `/api/auth/register` with that data.
3. Backend checks: email and password present, password passes validation, role is valid (Student/Mentor/Administrator).
4. Backend checks if email is already in the database; if yes, returns an error.
5. Password is **hashed** with bcrypt and stored with email, role, and name in the `users` collection.
6. Backend returns success; frontend can then redirect to login or auto-login (in our app we auto-login after register).

## 4.2 Login Flow

1. User enters email and password on the **Login** page.
2. Frontend sends **POST** to `/api/auth/login` with email and password.
3. Backend finds the user by email and checks the password against the stored hash.
4. If correct: backend creates a **JWT** (access token) that encodes the user’s ID, and returns the token plus user info (id, email, role, name).
5. Frontend saves the token in **localStorage** and user info in state (and optionally localStorage). From now on, every API request includes the token in the **Authorization** header.

## 4.3 Assessment Flow (FR2)

1. Student opens the **Assessment** page. Frontend sends **GET** to `/api/assessment/questions` with the JWT in the header.
2. Backend checks JWT and role; if the user is not a Student, returns 403. If OK, reads questions from `assessment_questions`, **removes the correct_answer** field, and returns the list.
3. Student answers each question; frontend stores selected option index per question.
4. On Submit, frontend sends **POST** to `/api/assessment/submit` with a list like `[{ question_id, selected_option }, ...]`.
5. Backend again checks JWT and Student role. It loads all questions, compares each selected_option to the stored correct_answer, computes scores per domain and overall, determines recommended domain(s), saves the result in the `assessments` collection, and returns the result (scores, recommended domain, etc.).
6. Frontend redirects to the **Result** page, which calls **GET** `/api/assessment/result` to fetch the latest result and displays it.

## 4.4 Session and Protected Routes

- **Session** = JWT token + user info. Token is sent on every request; backend uses it to identify the user.
- If the token is missing or invalid, the backend returns **401**. The frontend then clears token and user and redirects to the login page.
- **Protected routes** (e.g. Dashboard, Assessment, Result) only render if the user is logged in; otherwise the app redirects to login.

---

# PART 5 — WHICH FILES ARE RESPONSIBLE FOR WHAT

## Backend (Python / Flask)

| File                                         | Responsibility                                                                                                                                                |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/run.py`                             | Starts the Flask app. Entry point when you run the server.                                                                                                    |
| `backend/app/__init__.py`                    | Creates the Flask app, loads config, connects MongoDB, registers blueprints (auth and assessment), prints MongoDB connection log.                             |
| `backend/app/config.py`                      | Reads environment variables (e.g. MONGODB_URI, MONGODB_DB, SECRET_KEY, JWT settings). Single place for configuration.                                         |
| `backend/app/extensions.py`                  | Holds the MongoDB connection object (PyMongo) used across the app.                                                                                            |
| `backend/app/api/auth.py`                    | **FR1 API**: Register, Login, Logout, Profile. Each is a view (class) that receives the request and calls the auth service.                                   |
| `backend/app/api/assessment.py`              | **FR2 API**: Get questions, Submit answers, Get result. All require JWT + Student role.                                                                       |
| `backend/app/services/auth_service.py`       | **FR1 logic**: Hash password, check password, validate password strength, create user, authenticate user, get user by ID. No HTTP here — only business logic. |
| `backend/app/services/assessment_service.py` | **FR2 logic**: Get questions (and hide correct answer), submit answers and compute scores and recommendations, get latest result. Talks to MongoDB.           |
| `backend/app/utils/decorators.py`            | **RBAC**: `@role_required('Student')` — ensures the request has a valid JWT and that the user’s role is in the allowed list.                                  |
| `backend/seed_assessment.py`                 | One-time script to insert sample MCQ questions into `assessment_questions` (so the assessment has data).                                                      |

## Frontend (React)

| File                                                 | Responsibility                                                                                                                                                                                                                                     |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `frontend/src/App.jsx`                               | Defines routes: Home, Login, Register, Dashboard, Assessment, Result. Wraps app in AuthProvider. Protects dashboard/assessment/result with ProtectedRoute.                                                                                         |
| `frontend/src/main.jsx`                              | Renders the React app into the DOM and imports global CSS.                                                                                                                                                                                         |
| `frontend/src/context/AuthContext.jsx`               | **FR1 state**: Holds current user and loading. Provides login, logout, register. On load, reads token and user from localStorage to restore session.                                                                                               |
| `frontend/src/api/client.js`                         | Axios instance: base URL `/api`, adds JWT from localStorage to every request, handles 401 by clearing token and redirecting to login. Exposes `authApi` and `assessmentApi` for register, login, logout, profile, getQuestions, submit, getResult. |
| `frontend/src/components/ProtectedRoute.jsx`         | If not logged in → redirect to login. If role not allowed → redirect to dashboard. Otherwise renders children. Used for /dashboard, /assessment, /result.                                                                                          |
| `frontend/src/pages/Login.jsx`                       | Login form: email, password, submit. Calls `login()` from AuthContext, then redirects.                                                                                                                                                             |
| `frontend/src/pages/Register.jsx`                    | Register form: email, name, role (dropdown), password, confirm password. Calls `register()` then `login()`, then redirects to dashboard.                                                                                                           |
| `frontend/src/pages/Dashboard.jsx`                   | Shows greeting and role; for Students, links to Start Assessment and View Last Result. Uses DashboardLayout.                                                                                                                                       |
| `frontend/src/pages/Assessment.jsx`                  | Loads questions from API, shows one question at a time with options, stores selected option per question, submits to API and navigates to Result.                                                                                                  |
| `frontend/src/pages/Result.jsx`                      | Loads latest result from API and shows recommended domain, overall score, and table of scores by domain.                                                                                                                                           |
| `frontend/src/pages/Home.jsx`                        | Public landing: hero, Register/Login buttons, feature cards. No auth required.                                                                                                                                                                     |
| `frontend/src/components/layout/DashboardLayout.jsx` | Layout for logged-in pages: sidebar (nav + logout), main content area, right panel (profile + quick links).                                                                                                                                        |

---

# PART 6 — LOGIC BEHIND MAJOR FUNCTIONS (For Deep Understanding)

## 6.1 Password Hashing and Checking (auth_service)

- **hash_password**: Takes the plain password, generates a random “salt”, and runs bcrypt. The result is a string we store in the database. We never store the raw password.
- **check_password**: Takes the plain password and the stored hash. Bcrypt runs the same algorithm with the salt embedded in the hash; if the result matches the stored hash, the password is correct.

## 6.2 Password Validation (auth_service)

- **validate_password**: Returns (True, '') if valid, (False, error_message) if not. Rules: length ≥ 8, at least one uppercase, one lowercase, one digit. This is called in the Register API before creating the user.

## 6.3 Create User (auth_service)

- Check role is one of Student, Mentor, Administrator.
- Check email is not already in `users` collection.
- Build a document: email (lowercased), password_hash (from hash_password), role, name.
- Insert into `users`, then return a safe user object (id, email, role, name) — no password_hash.

## 6.4 Authenticate User (auth_service)

- Find user in `users` by email (lowercased).
- If not found, return None.
- If found, run check_password(entered_password, user.password_hash). If it fails, return None.
- If it passes, return user object (id, email, role, name) — no password in the response.

## 6.5 JWT and Session

- On login, backend calls `create_access_token(identity=user['id'])`. The “identity” is the user ID. The token is signed with the server’s secret; later the server can decode it and get back the user ID.
- Frontend stores this token. For every request, the client (in `client.js`) adds header: `Authorization: Bearer <token>`.
- Backend uses `@jwt_required()` to ensure the request has a valid token and to get the current user ID with `get_jwt_identity()`.

## 6.6 Role-Required Decorator (decorators.py)

- `@role_required('Student')` first runs `verify_jwt_in_request()` so we have a valid JWT.
- Gets user_id from the token, loads the user from the database, checks that `user.role` is in the allowed list (e.g. 'Student'). If not, returns 403 Forbidden.
- So “Session handling” = JWT; “Role-based access control” = this decorator + allowed roles per route.

## 6.7 Get Questions (assessment_service)

- Fetches all documents from `assessment_questions`.
- For each question, converts `_id` to string `id`, and **deletes** the `correct_answer` field so the frontend never sees it. Returns the list.

## 6.8 Submit Assessment (assessment_service)

- Receives list of `{ question_id, selected_option }`.
- Loads all questions and builds a map by question id.
- For each domain we keep: correct count, total count.
- For each answer: find the question, get its domain and correct_answer index. Increment total for that domain; if selected_option equals correct_answer, increment correct for that domain and for overall.
- Compute percentage per domain (correct/total \* 100) and overall.
- Sort domains by score descending; top domain = recommended_domain; top 3 = recommended_domains.
- Save one document in `assessments`: user_id, answers, domain_scores, overall_score, recommended_domain, recommended_domains, etc.
- Return the same result to the frontend (and frontend redirects to Result page).

## 6.9 Get Latest Result (assessment_service)

- Find one document in `assessments` for this user_id, sorted by \_id descending (newest first).
- Remove internal fields (\_id, user_id, answers) and return the rest (domain_scores, overall_score, recommended_domain, etc.) for the Result page to display.

---

# PART 7 — SUGGESTED DEMO FLOW (About 2–3 minutes)

Use this order so you show both FR1 and FR2 clearly.

1. **Start at Home**  
   Show the landing page. Say: "This is the public home page. From here users can go to Register or Login."

2. **Register (FR1)**  
   Click Register. Fill form: email, name, role = Student, password (that meets the rules). Submit. Say: "We register with a role; the backend validates the password and stores a hashed password. We’re now logged in and redirected to the dashboard."

3. **Dashboard and role (FR1)**  
   Show the dashboard. Say: "The dashboard shows the current user and role. Only Students see the assessment links; that’s role-based access."

4. **Assessment (FR2)**  
   Click "Start Assessment". Show one or two questions, pick an option, maybe go Next/Previous. Say: "Questions are loaded from the backend; the correct answer is never sent to the browser. I’ll submit at the end."

5. **Submit and result (FR2)**  
   Submit the assessment. Show the Result page: recommended domain, overall score, table of scores by domain. Say: "The backend calculated scores per domain and recommended the best-performing domain. This is the automated score calculation and domain recommendation."

6. **Logout (FR1)**  
   Log out from the sidebar. Say: "Logout clears the token and session. If I try to open the dashboard again, I’ll be redirected to login."

7. **Login (FR1)**  
   Log in again with the same user. Say: "Login returns a new JWT; the frontend stores it and uses it for all subsequent requests."

Optional: Show Register as Mentor or Administrator and open Dashboard to show they don’t see the Assessment/Result links (or that those routes redirect), to illustrate RBAC.

---

# QUICK REFERENCE — ONE-SENTENCE SUMMARY

- **FR1**: Users register with a role (Student/Mentor/Admin), log in to get a JWT; passwords are validated and hashed; the backend uses the token and role to control access (session + RBAC).
- **FR2**: Students take an MCQ test; the backend scores answers per domain and overall, saves the result, and recommends freelancing domains based on performance; the correct answers are never sent to the frontend.

Use this document as your script and reference while recording. Good luck with your prototype video.
