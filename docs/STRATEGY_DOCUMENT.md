# AI-Supported Virtual Internship Hub for Freelancing Careers

## Complete Strategy & Architecture Document

**Document Version:** 1.2  
**Date:** February 22, 2026  
**Author:** Senior Product Engineer / Tech Lead / UI/UX Architect

**Project Metadata (from SRS):**

- **Group Id:** F25PROJECT3E06F
- **Students:** Muhammad Awais, Anam Khalid
- **Supervisor:** Dr. Saima Munawar

---

## Executive Summary

This document outlines the complete strategy, architecture, development plan, and implementation approach for the **AI-Supported Virtual Internship Hub**—a centralized web platform that connects students with real-world freelance opportunities using AI for a personalized and productive experience. The platform provides students with simulated (and optionally real) freelancing experience, AI-powered assessment, personalized task recommendations, virtual workspace collaboration, and portfolio generation for platforms like Upwork and Fiverr. It also supports **Clients** who post projects, fund milestones via Escrow, and receive AI-recommended candidates.

---

# 1. REQUIREMENTS UNDERSTANDING

## 1.1 Project Goal (Restated)

The platform is an **AI-powered virtual internship hub** that:

1. **Connects students with opportunities** — Provides students with realistic project tasks across domains (graphic design, content writing, programming, etc.) from both simulated tasks and real client projects.
2. **Uses AI throughout** — For skill assessment, task recommendation, **recommending candidates to clients**, automated evaluation of submissions (code, plagiarism, grammar, design), and career guidance via chatbot.
3. **Connects stakeholders** — Students, **Clients**, Mentors, and Admins. Students work with mentors and clients; admins manage the ecosystem.
4. **Virtual Workspace** — Project-specific dashboards with real-time messaging, video calls, file sharing, version control, milestone setting, and progress tracking.
5. **Payment & Reputation System** — Secure Escrow where clients fund milestones in advance; funds released upon work approval. Reputation/ratings for students and clients.
6. **Produces tangible output** — Digital portfolios showcasing skills, education, and work samples for platforms like Upwork and Fiverr.
7. **Reduces dependency** — Delivers practical, evaluated experience with optional real-world client projects.

**Reference:** Upwork-style structure (job marketplace, profiles, portfolios, skill tags, proposals, escrow, messaging) adapted for virtual internships with AI evaluation and mentor oversight.

---

## PROTOTYPE SCOPE (Current Phase)

**Only the following two modules are to be implemented for the prototype. All other functionalities will be delivered in later project phases.**

| Module                                     | Functional Requirement                     | Status                           |
| ------------------------------------------ | ------------------------------------------ | -------------------------------- |
| **FR1**                                    | User Registration and Authentication       | In Scope                         |
| **FR2**                                    | Skill Assessment and Domain Recommendation | In Scope                         |
| FR3–FR10, Virtual Workspace, Payment, etc. | All other features                         | Deferred to final project phases |

**Prototype Deliverables:**

- Complete, working frontend and backend application folders
- Full integration between frontend and backend so both work together
- No placeholder or stub implementations for FR1 and FR2 — production-ready code

---

## 1.2 Actors & User Journeys

| Actor       | Description                                      | Primary Goals                                                                   |
| ----------- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Student** | Learner seeking practical freelancing experience | Complete tasks, receive feedback, build portfolio, graduate                     |
| **Client**  | Individual/company posting real projects         | Post projects, receive AI-recommended candidates, fund milestones, approve work |
| **Mentor**  | Experienced professional guiding students        | Review work, give feedback, approve submissions, track progress                 |
| **Admin**   | Platform operator                                | Manage users, projects, reports, moderation                                     |

### Student User Journey (High-Level)

```
Register → Login → Skill Assessment (AI) → Domain Recommendation →
Browse/Receive Tasks → Claim Task → Virtual Workspace (messaging, files, milestones) →
Submit Work → AI Auto-Evaluation → Mentor Review → Feedback → Iterate or Complete →
Portfolio Updated → Career Chatbot (optional) → Graduation
```

### Client User Journey (from SRS Scope)

```
Register → Login → Post Project (requirements, milestones, budget) →
Receive AI-Recommended Candidates → Select Student(s) → Fund Milestones (Escrow) →
Collaborate via Virtual Workspace (messaging, video, file sharing) →
Approve Work → Release Funds → Rate/Review
```

### Mentor User Journey

```
Register → Admin Approval → Login → Mentor Dashboard → View Assigned Students →
Review Submissions (with AI feedback visible) → Give Feedback → Approve/Reject →
Support students (AI chatbot assists with career tips) → View Analytics
```

### Admin User Journey

```
Login → Admin Panel → Manage Users (students, mentors, clients) →
Manage Projects/Tasks → Assign Students to Mentors → View Reports & Analytics →
Enable FR10 Integration (optional) → Moderation → System Config
```

---

## 1.3 Detailed User Stories & Acceptance Criteria

### FR1 / FR001: User Registration & Authentication (Prototype In Scope)

**Description:** This module enables access to the system for different types of users.

**User Roles (Prototype):** Student, Mentor, Administrator

**Features to be Implemented (Prototype):**

| Feature                              | Implementation Notes                                                                                                        |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **Role-based user registration**     | Registration form with role selection (Student, Mentor, Administrator); each role gets appropriate default permissions      |
| **Login and logout**                 | Login form (email + password); logout clears session/tokens; redirect to role-specific dashboard                            |
| **Password validation/check**        | Client- and server-side validation; strength rules (e.g., min length, complexity); secure storage (bcrypt/argon2)           |
| **Role-based access control (RBAC)** | Routes and API endpoints protected by role; Student/Mentor/Admin see different UIs and have different permissions           |
| **Session handling**                 | JWT (access + refresh) or server-side sessions; session timeout; secure cookie/storage; persist login across page refreshes |

| ID    | User Story                                                                                                    | Acceptance Criteria                                                          |
| ----- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| US1.1 | As a **student**, I want to register with email and password so that I can access the platform                | ✓ Email validation; password strength rules; role=student; unique email      |
| US1.2 | As a **mentor**, I want to register with email and password so that I can guide students                      | ✓ Same auth flow; role=mentor; admin approval can be deferred to later phase |
| US1.3 | As an **administrator**, I want to register/log in with elevated privileges so that I can manage the platform | ✓ Admin-only routes; role=administrator; JWT/session-based auth              |
| US1.4 | As any user, I want to log in and stay logged in across sessions                                              | ✓ JWT refresh; secure logout; session timeout configurable                   |
| US1.5 | As a user, I want my password validated before account creation                                               | ✓ Password strength check; confirmation field; server-side validation        |

_Note: Client role and forgot-password flow are deferred to later phases._

### FR2 / FR002: Skill Assessment & Domain Recommendation (Prototype In Scope)

**Description:** This module evaluates a student's skills through an assessment test and recommends suitable freelancing domains.

**Assessment Areas (DigiSkills / Enrolled Courses):**

| Domain                 | Description                                    |
| ---------------------- | ---------------------------------------------- |
| Graphic Design         | Design principles, tools, visual communication |
| Content Writing        | Writing quality, structure, SEO basics         |
| Programming            | Logic, syntax, problem-solving                 |
| Freelancing            | Proposals, client management, pricing          |
| E-Commerce             | Online selling, platforms, marketing           |
| QuickBooks             | Accounting, invoicing, bookkeeping             |
| AutoCAD                | CAD basics, technical drawing                  |
| Other relevant domains | Extensible for additional domains              |

**Features to be Implemented (Prototype):**

| Feature                                        | Implementation Notes                                                                                               |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Online skill assessment test (MCQs)**        | Multiple-choice questions per domain; question bank; one question per screen or paginated; timer optional          |
| **Automated score calculation**                | Server-side scoring; correct/incorrect per question; per-domain scores; overall score                              |
| **Display of recommended freelancing domains** | Based on performance (highest scores); show top 1–3 domains; optionally show scores per domain; store result in DB |

| ID    | User Story                                                                                                             | Acceptance Criteria                                                                                                               |
| ----- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| US2.1 | As a **student**, I want to take an online skill assessment test (MCQs) so that I get a recommended freelancing domain | ✓ MCQ format; questions across selected domains; submit answers; automated scoring                                                |
| US2.2 | As a **student**, I want to see my recommended freelancing domains based on my performance                             | ✓ Result page; recommended domain(s) displayed; scores per domain; result stored (user_id, scores, recommended_domain, timestamp) |
| US2.3 | As a **student**, I want my scores to be calculated automatically when I submit the test                               | ✓ Server-side calculation; correct answers mapped; no manual grading                                                              |

### FR3 / FR003: AI Task/Project Allocation

| ID    | User Story                                                                       | Acceptance Criteria                                                                                                                           |
| ----- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| US3.1 | As a **student**, I want tasks recommended based on my profile and progress      | ✓ Recommendation engine uses: domain, completed tasks, skill level, performance; returns ranked task list                                     |
| US3.2 | As a **client**, I want AI to recommend suitable candidates for my project       | ✓ AI analyzes project requirements and student profiles; returns ranked candidate list (SRS: "recommend most suitable candidates to clients") |
| US3.3 | As a **student**, I can browse all available tasks filtered by domain/difficulty | ✓ Filtering; pagination; task cards with metadata                                                                                             |
| US3.4 | As a **student**, I can claim/start a task                                       | ✓ Task assignment; status=in_progress; deadline set                                                                                           |
| US3.5 | As **admin**, I can create and manage tasks/projects                             | ✓ CRUD for tasks; difficulty, domain, instructions, attachments                                                                               |

### FR4 / FR004: Automated AI Evaluation of Submissions

| ID    | User Story                                                                            | Acceptance Criteria                                                                    |
| ----- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| US4.1 | As a **student**, I submit my work (code/file/text) and receive AI-generated feedback | ✓ Upload support; AI evaluation pipeline; feedback returned; plagiarism check for text |
| US4.2 | As system, code submissions are checked for correctness and style                     | ✓ Linting; test execution (if applicable); structure analysis                          |
| US4.3 | As system, text submissions are checked for grammar and plagiarism                    | ✓ NLP grammar check; similarity scoring against corpus                                 |
| US4.4 | As system, design submissions are evaluated for quality (if feasible)                 | ✓ Basic heuristics or model-based scoring; fallback to mentor-only                     |

### FR5 / FR006: Mentor Dashboard

| ID    | User Story                                                                              | Acceptance Criteria                                                                              |
| ----- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| US5.1 | As a **mentor**, I see a dashboard of my assigned students                              | ✓ Student list; progress summary; pending reviews count                                          |
| US5.2 | As a **mentor**, I can track student progress, review submissions, and provide feedback | ✓ View submission; add text/video feedback; approve/reject (SRS FR006: "track" student progress) |
| US5.3 | As a **mentor**, I can see AI evaluation results to inform my feedback                  | ✓ AI feedback visible; mentor can override or supplement                                         |

### FR6 / FR005: Portfolio Generation

| ID    | User Story                                                          | Acceptance Criteria                                                                  |
| ----- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| US6.1 | As a **student**, I want a portfolio built from my completed tasks  | ✓ Portfolio page; projects/tasks with descriptions, outcomes, skills; shareable link |
| US6.2 | As a **student**, I can export my portfolio for Upwork/Fiverr       | ✓ Export as PDF or structured JSON; compatible format                                |
| US6.3 | As a **student**, I can customize portfolio sections and visibility | ✓ Toggle projects; reorder; add bio (optional)                                       |

### FR7 / FR007: AI Chatbot for Career Guidance

| ID    | User Story                                                                                     | Acceptance Criteria                                                                       |
| ----- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| US7.1 | As a **student**, I can chat with an AI assistant for career guidance and freelancing tips     | ✓ Chat interface; conversational responses; context-aware                                 |
| US7.2 | As a **mentor**, I can support students while the AI chatbot provides career tips and guidance | ✓ Mentors supplement chatbot; both available for student support (SRS FR007) “ask mentor” |
| US7.3 | As system, chatbot uses curated knowledge base and safe prompts                                | ✓ RAG or rule-based; no harmful content; fallback to ask mentor                           |
| US7.4 | As a **student**, I can ask about Upwork/Fiverr best practices                                 | ✓ Answers about profiles, proposals, pricing; sourced from docs                           |

### Virtual Workspace (SRS Scope — Project-Specific Dashboard)

| ID  | User Story                                                           | Acceptance Criteria                                              |
| --- | -------------------------------------------------------------------- | ---------------------------------------------------------------- |
| VW1 | As a **student/client**, I want real-time messaging within a project | ✓ Chat per project; WebSocket or polling; message history        |
| VW2 | As a **student/client**, I want video calls for collaboration        | ✓ WebRTC or third-party (Daily.co, Jitsi); join from workspace   |
| VW3 | As a **student/client**, I want file sharing and version control     | ✓ Upload files; version history; download previous versions      |
| VW4 | As a **client**, I want to set milestones and track progress         | ✓ Create milestones; student marks progress; client views status |
| VW5 | As a **student**, I want a project-specific dashboard                | ✓ Tasks, messages, files in integrated workspace view            |

### Payment & Reputation System (SRS Scope)

| ID  | User Story                                                          | Acceptance Criteria                                           |
| --- | ------------------------------------------------------------------- | ------------------------------------------------------------- |
| PR1 | As a **client**, I want to fund milestones in advance via Escrow    | ✓ Secure Escrow; client deposits; funds held until approval   |
| PR2 | As a **client**, I want to release funds upon student work approval | ✓ Approve milestone → release to student; audit trail         |
| PR3 | As a **student/client**, I want to rate and review after completion | ✓ Rating (1–5); optional text review; visible on profile      |
| PR4 | As system, reputation scores are computed and displayed             | ✓ Aggregate rating; completed project count; trust indicators |

### FR8 / FR008: Admin Panel

| ID    | User Story                                                    | Acceptance Criteria                                             |
| ----- | ------------------------------------------------------------- | --------------------------------------------------------------- |
| US8.1 | As **admin**, I can manage users (students, clients, mentors) | ✓ List, create, edit, deactivate users; bulk actions            |
| US8.2 | As **admin**, I can manage projects and tasks                 | ✓ CRUD; publish/unpublish; assign to domains                    |
| US8.3 | As **admin**, I can view system reports                       | ✓ User stats; task completion rates; AI usage; moderation queue |
| US8.4 | As **admin**, I can assign students to mentors                | ✓ Assignment interface; reassignment                            |

### FR9 / FR009: Reporting & Analytics

| ID    | User Story                                                          | Acceptance Criteria                                                   |
| ----- | ------------------------------------------------------------------- | --------------------------------------------------------------------- |
| US9.1 | As a **student**, I see my progress (completed tasks, skill trends) | ✓ Dashboard with charts; completion rate; skill improvement over time |
| US9.2 | As a **mentor**, I see analytics for my students                    | ✓ Aggregated progress; comparison; weak areas                         |
| US9.3 | As **admin**, I see platform-wide analytics                         | ✓ KPIs; user growth; task funnel; AI evaluation stats                 |

### FR10 / FR010: Integration with External Freelancing Platforms (Optional)

| ID     | User Story                                                         | Acceptance Criteria                                                      |
| ------ | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| US10.1 | As a **student**, I can link my Upwork/Fiverr profile              | ✓ OAuth or manual link; display on portfolio                             |
| US10.2 | As system, portfolio can be formatted for external platform export | ✓ One-click export; schema alignment with Upwork/Fiverr profile sections |

---

## 1.4 Assumptions & Edge Cases

### Assumptions

- Students have basic digital literacy and access to a modern browser.
- Mentors are vetted by admin before activation.
- AI models (skill assessment, evaluation, chatbot) can run on GPU or cloud API (e.g., OpenAI, local models).
- MongoDB is acceptable for document-oriented data; no complex relational joins required.
- File submissions are bounded in size (e.g., max 50MB per submission).
- Portfolio export does not require real-time sync with Upwork/Fiverr APIs (export as static artifact).
- Single-tenant deployment initially; multi-tenant can be phased later.
- English as primary language for MVP; i18n can be added later.

### Edge Cases to Handle

| Edge Case                                | Mitigation                                                      |
| ---------------------------------------- | --------------------------------------------------------------- |
| AI service failure during evaluation     | Fallback: queue for manual mentor review; retry with backoff    |
| Large file uploads                       | Chunked upload; virus scan; size limits; storage quota per user |
| Plagiarism check returns inconclusive    | Show “manual review needed”; flag for mentor                    |
| Student submits after deadline           | Allow with late flag; mentor decides whether to accept          |
| Mentor unassigns or goes inactive        | Admin reassigns; orphaned students go to pool                   |
| Chatbot receives harmful/off-topic input | Moderation layer; redirect to “ask mentor” or “contact support” |
| Skill assessment gaming                  | Randomize question order; time limits; anomaly detection        |
| Concurrent task claims                   | Optimistic locking; “task no longer available” message          |

---

## 1.5 Non-Functional Requirements (NFRs)

Aligned with SRS NFR001–NFR010:

| NFR    | SRS Label       | Description                                                                                       |
| ------ | --------------- | ------------------------------------------------------------------------------------------------- |
| NFR001 | System Speed    | Platform responds quickly; pages load in a few seconds                                            |
| NFR002 | Scalability     | System handles multiple users simultaneously without slowing down                                 |
| NFR003 | Reliability     | System works correctly without frequent errors or crashes                                         |
| NFR004 | Security        | User data safe; accounts protected with secure login and password management (JWT, bcrypt, HTTPS) |
| NFR005 | Usability       | Platform easy to use and understand for students, mentors, admins, and clients                    |
| NFR006 | Maintainability | System easy to update and maintain by developers; clear code structure                            |
| NFR007 | Compatibility   | Platform works on different browsers and devices (desktops, laptops, tablets)                     |
| NFR008 | Availability    | System accessible most of the time with minimal downtime (target 99%)                             |
| NFR009 | Portability     | System easy to move or deploy on different servers/cloud environments (Docker)                    |
| NFR010 | Documentation   | Clear user manuals and technical documentation for students, mentors, developers                  |

---

## 1.6 Adopted Methodology (from SRS)

This project follows a **Hybrid Approach** combining Prototype Model and Spiral Model:

- **Prototype Model** — Quick mockups of AI assessment, chatbot, mentor dashboard, and task allocation for early feedback.
- **Spiral Model** — Iterative development; risk handling (AI errors, model accuracy); continuous improvement via testing and evaluation.

This hybrid approach ensures faster development, early user validation, and better risk management during AI integration.

---

## 1.7 SRS Usage Scenarios Reference (UC01–UC08)

| UC   | Scenario                        | Actors                                           | Main Flow                                                        |
| ---- | ------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------- |
| UC01 | User Signup                     | Student / Mentor / Admin                         | Select signup → Enter details → Submit form                      |
| UC02 | Login                           | Student / Mentor / Admin                         | Select login → Enter credentials → Submit                        |
| UC03 | AI Skill Assessment             | Student                                          | Select AI Skill Test → Answer questions → Submit test            |
| UC04 | AI Task Allocation              | AI System / Student                              | AI analyzes skills → AI ranks tasks → Student selects task       |
| UC05 | Task Submission & AI Evaluation | Student                                          | Select task → Upload file → Submit for evaluation                |
| UC06 | Portfolio Generation            | Student                                          | Select portfolio → System compiles results → Portfolio generated |
| UC07 | Admin Management                | **Admin** (not Student; corrected from SRS typo) | Open admin panel → Manage users/projects → Add/Update/Delete     |
| UC08 | Career Guidance via AI Chatbot  | Student / AI Chatbot                             | Open AI Chatbot → Ask for guidance → Receive response            |

---

# 2. PROPOSED ARCHITECTURE

## 2.1 Flask vs Django — Decision

**Recommended: Flask + Flask-RESTX (or FastAPI)**

| Factor            | Flask                          | Django                                       |
| ----------------- | ------------------------------ | -------------------------------------------- |
| Flexibility       | High — add only what you need  | Opinionated — full-stack, more boilerplate   |
| AI/ML integration | Easy — plain Python services   | Possible but more wiring                     |
| Async support     | Flask 2.x async; or FastAPI    | Django async views (newer)                   |
| MongoDB           | Native via PyMongo/MongoEngine | Requires djongo or raw PyMongo; less natural |
| API-first         | Flask-RESTX, Connexion         | Django REST Framework ( heavier )            |
| Learning curve    | Lighter                        | Heavier                                      |
| Prototyping speed | Faster for custom logic        | Slower for non-CRUD flows                    |

**Verdict:** **Flask** (or **FastAPI** if you prefer async-native) — better fit for MongoDB, custom AI pipelines, and API-first design. Django is excellent for content-heavy admin, but we can achieve similar admin via Flask-Admin or custom React admin.

**Alternative:** FastAPI — if you want native async, automatic OpenAPI, and Pydantic validation out of the box. Slightly steeper learning curve but excellent for APIs.

---

## 2.2 Backend Architecture

- **API Style:** REST (GraphQL can be added later if needed; REST is sufficient for MVP)
- **Auth:** JWT (access + refresh); optional OAuth for social login (phase 2)
- **Roles:** Student, Client, Mentor, Admin — enforced via decorators/middleware
- **Services:**
  - `AuthService` — login, register, token refresh, password reset
  - `UserService` — profile, role assignment
  - `AssessmentService` — skill test, domain recommendation (AI)
  - `TaskService` — CRUD, assignment, recommendation (AI); candidate recommendation for clients
  - `SubmissionService` — upload, store, trigger evaluation
  - `EvaluationService` — AI pipeline (code, text, plagiarism, design)
  - `MentorService` — assignments, feedback, approvals
  - `PortfolioService` — generate, export
  - `ChatbotService` — LLM/RAG integration
  - `AnalyticsService` — aggregates, reports
  - `WorkspaceService` — project messaging, video calls, file sharing, version control, milestones
  - `PaymentService` — Escrow, milestone funding, fund release, reputation/ratings
- **Queue:** Celery + Redis for async AI evaluation and heavy jobs
- **Caching:** Redis for sessions, rate limiting, and hot data

---

## 2.3 Frontend Architecture

- **Framework:** React 18+
- **Routing:** React Router v6
- **State:** React Query (TanStack Query) for server state; Zustand or Context for UI state
- **Component Library:** Material UI (MUI) or Chakra UI — professional, accessible, theming
- **Layout System:** Responsive grid; sidebar for mentor/admin; top nav for students
- **Forms:** React Hook Form + Zod (validation)
- **Charts:** Recharts or Chart.js for analytics
- **File Upload:** react-dropzone or custom with progress
- **Styling:** CSS Modules or Tailwind (optional) + component library tokens

---

## 2.4 AI Architecture

| Component                      | Purpose                           | Tech Choice                                                      | Data Flow                                                   |
| ------------------------------ | --------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------- |
| **Skill Assessment**           | Map answers → domain + confidence | Scikit-learn (clustering/classification) or rule-based scoring   | Test answers → model → domain label                         |
| **Task Recommendation**        | Rank tasks for student            | Collaborative filtering or content-based (TF-IDF + cosine)       | User profile + progress → ranking → task IDs                |
| **Candidate Recommendation**   | Recommend students to clients     | Content-based (project reqs vs profiles); TF-IDF + cosine        | Project requirements + student profiles → ranked candidates |
| **Code Evaluation**            | Correctness, style                | AST parsing, linters (e.g., pylint, ESLint), test runners        | Code string → analysis → score + feedback                   |
| **Text/Plagiarism**            | Grammar, similarity               | NLTK/SpaCy (grammar); difflib/sentence-transformers (similarity) | Text → pipeline → score + feedback                          |
| **Design Evaluation**          | Basic quality heuristics          | Rule-based (resolution, format) or simple CNN (optional)         | Image → checks → score                                      |
| **Chatbot**                    | Career guidance                   | LLM (OpenAI/ Llama) + RAG over docs; fallback to rule-based      | User message → RAG → LLM → response                         |
| **Scalable Search (optional)** | Portfolio similarity search       | FAISS over embeddings                                            | Query → FAISS → similar portfolios                          |

**Model Strategy:**

- Prefer lightweight models for MVP (e.g., sentence-transformers for embeddings, small LLM for chatbot).
- Use cloud APIs (OpenAI, etc.) if budget allows; otherwise local models (Ollama, transformers).
- Implement fallbacks: if AI fails → queue for mentor review.

---

## 2.5 Data Model (MongoDB Collections)

| Collection            | Purpose                                        | Key Fields                                                   | Indexes                    |
| --------------------- | ---------------------------------------------- | ------------------------------------------------------------ | -------------------------- |
| `users`               | All users (students, clients, mentors, admins) | email, password_hash, role, profile, created_at              | email (unique), role       |
| `assessments`         | Skill test attempts                            | user_id, answers, domain_result, score, created_at           | user_id                    |
| `tasks`               | Available tasks                                | title, domain, difficulty, instructions, attachments, status | domain, difficulty, status |
| `assignments`         | Student-task link                              | student_id, task_id, status, claimed_at, deadline            | student_id, task_id        |
| `submissions`         | Submitted work                                 | assignment_id, user_id, files, text, status, ai_feedback     | assignment_id, user_id     |
| `evaluations`         | AI evaluation results                          | submission_id, scores, feedback, plagiarism_flag             | submission_id              |
| `mentor_feedback`     | Mentor reviews                                 | submission_id, mentor_id, feedback, approved                 | submission_id              |
| `portfolios`          | Student portfolios                             | user_id, projects[], visibility, updated_at                  | user_id                    |
| `chat_sessions`       | Chatbot conversations                          | user_id, messages[], created_at                              | user_id                    |
| `projects`            | Client-posted projects                         | client_id, title, requirements, milestones[], budget, status | client_id, status          |
| `project_messages`    | Workspace chat                                 | project_id, sender_id, content, created_at                   | project_id                 |
| `project_files`       | File sharing + versions                        | project_id, file_path, version, uploaded_by                  | project_id                 |
| `escrow_transactions` | Payment/Escrow                                 | project_id, milestone_id, amount, status, released_at        | project_id                 |
| `reviews`             | Reputation/ratings                             | reviewer_id, reviewee_id, project_id, rating, text           | reviewee_id, project_id    |
| `audit_logs`          | Security/compliance                            | action, user_id, resource, timestamp                         | user_id, timestamp         |

**Relations:**

- Users → Assessments (1:N)
- Users → Assignments (1:N)
- Tasks → Assignments (1:N)
- Assignments → Submissions (1:N, typically 1:1 per assignment)
- Submissions → Evaluations (1:1)
- Submissions → Mentor Feedback (1:1)
- Users → Portfolios (1:1)

---

## 2.6 File Storage Strategy

**Recommended: Local filesystem + optional S3 later**

| Approach                      | Pros                                 | Cons                                        |
| ----------------------------- | ------------------------------------ | ------------------------------------------- |
| **Local + GridFS**            | Simple; MongoDB native; good for MVP | Not ideal for multi-node; backup complexity |
| **Local directory**           | Very simple; easy debugging          | Scale limits; no CDN                        |
| **S3-compatible (MinIO/AWS)** | Scalable; CDN-ready; versioning      | Setup; cost                                 |

**Proposal:**

- **MVP:** Store files in `uploads/` directory; path stored in `submissions.files[].path`
- **Beta:** Migrate to MinIO (S3-compatible) in Docker for dev/staging
- **Production:** AWS S3 or equivalent; signed URLs for secure access
- **Virus scan:** Integrate ClamAV or cloud scanning for uploads

---

## 2.7 Analytics Computation

- **Aggregation pipeline** in MongoDB for counts, averages, trends
- **Precomputed metrics** via scheduled Celery tasks (e.g., daily student progress snapshot)
- **Real-time dashboards:** API endpoints that run aggregations on request (with caching for heavy queries)
- **Stored reports:** Admin can generate and download CSV/PDF reports

---

# 3. FULL DEVELOPMENT PLAN (A TO Z)

## 3.1 Prototype Phase (Current — FR1 & FR2 Only)

**Goal:** Implement FR1 and FR2 with full frontend–backend integration. Both must work together end-to-end.

| Feature                   | Milestone                                          | Frontend                                                                                                                 | Backend                                                                                              | Integration                                                                     |
| ------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **FR1: Auth**             | Register, login, logout, RBAC, session             | Registration form (role selection); Login form; Logout button; Protected routes by role; Role-based dashboard redirect   | User model; Auth endpoints (register, login, logout); JWT/session; Password hashing; RBAC middleware | API calls from frontend; token storage; role-based routing; session persistence |
| **FR2: Skill Assessment** | MCQ test; automated scoring; domain recommendation | Assessment test UI (MCQs); Result page (recommended domains, scores); Navigation from login to assessment (for students) | Assessment questions; Submit endpoint; Scoring logic; Domain recommendation logic; Store results     | Submit answers → backend scores → return result → display recommendations       |

**Prototype Structure (Folders):**

- `frontend/` — React app with auth and assessment pages
- `backend/` — Flask/Django API with auth and assessment modules
- Both must run together (e.g., via Docker or separate dev servers with CORS configured)

**Prototype User Roles:** Student, Mentor, Administrator (Client deferred)

**Prototype Data:**

- `users` collection (email, password_hash, role, name, created_at)
- `assessment_questions` collection (question, options, correct_answer, domain)
- `assessments` collection (user_id, answers, scores, recommended_domain, created_at)

**Prototype API Endpoints:**

- `POST /api/auth/register` — { email, password, role, name }
- `POST /api/auth/login` — { email, password } → { access_token, user: { id, email, role } }
- `POST /api/auth/logout` — (authenticated) invalidate session
- `GET /api/assessment/questions` — (authenticated, student) return MCQ questions
- `POST /api/assessment/submit` — (authenticated, student) { answers } → { scores, recommended_domain }
- `GET /api/assessment/result` — (authenticated, student) last assessment result

**Prototype Workflow:**

1. User visits app → Register or Login (role: Student, Mentor, Administrator)
2. After login → Redirect to role-specific landing (Student → Assessment; Mentor/Admin → placeholder dashboard)
3. Student takes assessment → Answer MCQs → Submit → Backend scores and computes recommended domain → Display result
4. Logout → Clear session → Redirect to login

---

## 3.2 Development Phases (Full Project — Post-Prototype)

### Phase 1: MVP (8–10 weeks)

**Goal:** Core flows work end-to-end

| Feature                      | Milestone                                               | Dependencies                   |
| ---------------------------- | ------------------------------------------------------- | ------------------------------ |
| Auth (FR1)                   | Users can register/login as student/client/mentor/admin | DB, JWT                        |
| Skill assessment (FR2)       | Basic test → domain recommendation                      | MongoDB, simple scoring        |
| Task CRUD + assignment (FR3) | Admin creates tasks; students claim                     | Tasks, Assignments collections |
| Submission + AI eval (FR4)   | Upload; basic code/text evaluation                      | File storage, AI services      |
| Mentor dashboard (FR5)       | View students; approve/reject; feedback                 | Mentor assignments             |
| Portfolio (FR6)              | Generate from completed tasks                           | Portfolio collection           |
| Admin panel (FR8)            | User and task management (incl. clients)                | RBAC                           |
| Virtual Workspace (SRS)      | Real-time messaging; file sharing; milestones           | WebSocket or polling           |
| Payment/Escrow (SRS)         | Milestone funding; release; basic ratings               | Payment integration            |

**Deliverables:** Deployable app; basic Docker setup; README.

---

### Phase 2: Beta (4–6 weeks)

**Goal:** Polish, analytics, chatbot

| Feature                    | Milestone                         | Dependencies          |
| -------------------------- | --------------------------------- | --------------------- |
| Chatbot (FR7)              | Career guidance; freelancing tips | LLM/RAG               |
| Analytics (FR9)            | Student/mentor/admin dashboards   | Aggregation pipelines |
| Plagiarism + grammar (FR4) | Enhanced text evaluation          | NLP pipeline          |
| Export portfolio (FR6)     | PDF/JSON export                   | Export service        |
| Virtual Workspace (full)   | Video calls; version control      | WebRTC or Jitsi       |
| UI/UX refinement           | Responsive; accessibility         | Design review         |
| Testing                    | Unit + integration tests          | pytest, Jest          |

**Deliverables:** Beta release; user testing; bug fixes.

---

### Phase 3: Final (4–6 weeks)

**Goal:** Production-ready; optional integrations

| Feature            | Milestone                              | Dependencies        |
| ------------------ | -------------------------------------- | ------------------- |
| FR10 (optional)    | Link external profiles; export formats | OAuth; API research |
| FAISS (optional)   | Portfolio search                       | Embeddings; FAISS   |
| Security hardening | Penetration testing; rate limits       | Security checklist  |
| CI/CD              | Automated tests; deployment pipeline   | GitHub Actions      |
| Documentation      | API docs; user guide                   | OpenAPI; docs site  |

**Deliverables:** Production release; handover docs.

---

## 3.2 Coding Standards

- **Python:** PEP 8; Black for formatting; isort for imports; type hints where practical
- **JavaScript/React:** ESLint (recommended config); Prettier; functional components + hooks
- **Naming:** `snake_case` (Python); `camelCase` (JS); `PascalCase` (components)
- **Git:** Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
- **Branching:** GitFlow or GitHub Flow — `main` (prod), `develop` (integrate), `feature/*`, `fix/*`

---

## 3.3 Testing Strategy

| Type        | Scope                                  | Tools                         |
| ----------- | -------------------------------------- | ----------------------------- |
| Unit        | Services, utilities                    | pytest (Python), Jest (React) |
| Integration | API endpoints, DB                      | pytest + requests; test DB    |
| E2E         | Critical flows (login, submit, review) | Playwright or Cypress         |
| Load        | Key endpoints                          | Locust or k6                  |

**Coverage target:** 70%+ for critical paths.

---

## 3.4 Linting, Formatting, CI/CD

- **Linting:** Ruff (Python), ESLint (JS)
- **Formatting:** Black, Prettier
- **CI:** GitHub Actions — lint, format, test on push/PR
- **CD:** Build Docker image; deploy to staging on merge to `develop`; manual promote to prod

---

## 3.5 Deployment Plan

- **Containers:** Docker + Docker Compose (app, MongoDB, Redis, Celery worker, nginx)
- **Environments:** `.env.example`; separate configs for dev, staging, prod
- **Secrets:** Environment variables; no secrets in repo
- **Database:** MongoDB replica set for prod (optional in MVP)

---

# 4. DETAILED WORKFLOWS

## 4.0 Prototype Flow (FR1 & FR2 Only — Current Phase)

**Student:**

```
1. Register (email, password, role=Student) → Login
2. Redirect to Assessment page
3. Take MCQ skill assessment → Submit answers
4. Backend scores → Returns recommended domain(s) + scores
5. Display result page (recommended domains, per-domain scores)
6. Logout
```

**Mentor:**

```
1. Register (role=Mentor) or Login → Redirect to Mentor placeholder dashboard
2. Logout
```

**Administrator:**

```
1. Register (role=Administrator) or Login → Redirect to Admin placeholder dashboard
2. Logout
```

---

## 4.1 Student Flow (Full — Post-Prototype)

```
1. Register → Verify email (optional) → Login
2. Onboarding: Complete profile (name, education, interests)
3. Take skill assessment (10–15 questions, ~10 min)
4. Receive domain recommendation (e.g., "Content Writing – Intermediate")
5. Browse recommended tasks; filter by domain/difficulty
6. Claim a task → Deadline set (e.g., 7 days)
7. Work on task; upload files or paste code/text
8. Submit → AI evaluation runs (async)
9. View AI feedback; wait for mentor review
10. Mentor approves or requests changes → Iterate if needed
11. On approval: Task marked complete; portfolio updated
12. Repeat 5–11 for more tasks
13. Use chatbot anytime for career tips
14. View portfolio; export for Upwork/Fiverr
15. Graduation (optional: badge/certificate when threshold met)
```

---

## 4.2 Mentor Flow

```
1. Register → Admin approves → Login
2. Mentor dashboard: List of assigned students
3. View pending submissions (AI feedback visible)
4. Open submission → Review work + AI feedback
5. Add written/video feedback; Approve or Request changes
6. Student notified; resubmission if requested
7. View analytics: Student progress, completion rates, skill trends
8. Optionally: Request more students from admin
```

---

## 4.3 Client Flow (from SRS Scope)

```
1. Register → Login
2. Post project (requirements, milestones, budget)
3. Receive AI-recommended candidates → Select student(s)
4. Fund milestones via Escrow
5. Collaborate via Virtual Workspace (messaging, video, file sharing)
6. Track progress; approve work
7. Release funds upon approval
8. Rate and review student
```

---

## 4.4 Admin Flow

```
1. Login → Admin panel
2. Users: List students/mentors; create, edit, deactivate; assign students to mentors
3. Projects/Tasks: CRUD; publish/unpublish; assign domains
4. Reports: User growth, task funnel, AI evaluation stats, moderation queue
5. System: Config (e.g., assessment cooldown, file limits); view audit logs
6. Moderation: Flagged content; user reports (if applicable)
```

---

## 4.5 AI Workflow

```
1. Data collection: Assessments (answers), submissions (code/text/images)
2. Preprocessing: Normalize, sanitize, chunk if needed
3. Model selection:
   - Skill assessment: Rule-based or simple ML (e.g., Random Forest)
   - Task recommendation: Content-based (TF-IDF + cosine) or collaborative
   - Code: AST + linter output
   - Text: NLTK/SpaCy + similarity (e.g., sentence-transformers)
   - Chatbot: LLM with RAG over career docs
4. Evaluation: Run model; extract score + feedback
5. Fallback: On error → queue for mentor review; log failure
6. Feedback storage: Save in `evaluations` collection; link to submission
```

---

## 4.6 Chatbot Workflow

```
1. User sends message → Validate input (length, content filter)
2. Retrieve context: User profile, recent tasks, conversation history
3. RAG: Query knowledge base (career docs, freelancing tips) → Top-k chunks
4. Prompt: System + context + user message → LLM
5. Post-process: Sanitize response; check for harmful content
6. Store message in chat_sessions
7. Return response to user
8. Fallback: "I'm unsure. Consider asking your mentor." or escalate
```

**Knowledge sources:** Curated Markdown/PDF docs on Upwork/Fiverr best practices, proposal writing, portfolio tips.

---

# 5. PROJECT STRUCTURE (FINAL PROPOSED)

## 5.1 Root Structure

```
ai-internship-hub/
├── frontend/                 # React application
├── backend/                  # Flask/FastAPI application
├── ai_services/              # Shared AI modules (or inside backend)
├── shared/                   # Shared schemas, types (optional)
├── tests/                    # E2E and cross-cutting tests
├── docs/                     # Documentation
├── docker/                   # Docker configs
├── .github/                  # CI/CD workflows
├── docker-compose.yml
├── .env.example
├── README.md
└── STRATEGY_DOCUMENT.md      # This document
```

---

## 5.2 Frontend (React)

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/                  # API client functions
│   │   ├── auth.ts
│   │   ├── tasks.ts
│   │   ├── submissions.ts
│   │   └── ...
│   ├── components/           # Reusable UI components
│   │   ├── common/           # Button, Input, Modal, etc.
│   │   ├── layout/           # Header, Sidebar, Footer
│   │   └── domain/           # Domain-specific (TaskCard, PortfolioView)
│   ├── pages/                # Route-level pages
│   │   ├── auth/             # Login, Register
│   │   ├── student/          # Dashboard, Tasks, Submissions, Portfolio
│   │   ├── client/           # Projects, Candidates, Workspace, Escrow
│   │   ├── mentor/           # Dashboard, Reviews, Analytics
│   │   └── admin/            # Users, Tasks, Reports
│   ├── hooks/                # Custom hooks
│   ├── stores/               # Zustand/Context stores
│   ├── utils/                # Helpers, validation
│   ├── types/                # TypeScript types
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .eslintrc.js
```

---

## 5.3 Backend (Flask)

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py             # Configuration by env
│   ├── extensions.py         # Flask extensions (JWT, Mongo, etc.)
│   ├── models/               # Mongo document schemas
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── submission.py
│   │   └── ...
│   ├── api/                  # API blueprints
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   ├── submissions.py
│   │   ├── mentors.py
│   │   ├── portfolio.py
│   │   ├── chatbot.py
│   │   └── admin.py
│   ├── services/             # Business logic
│   │   ├── auth_service.py
│   │   ├── assessment_service.py
│   │   ├── task_service.py
│   │   ├── evaluation_service.py
│   │   └── ...
│   ├── ai/                   # AI pipelines
│   │   ├── skill_assessment.py
│   │   ├── task_recommender.py
│   │   ├── code_evaluator.py
│   │   ├── text_evaluator.py
│   │   └── chatbot.py
│   ├── tasks/                # Celery tasks
│   │   ├── evaluate_submission.py
│   │   └── ...
│   └── utils/                # Helpers
│       ├── validation.py
│       └── security.py
├── migrations/               # Optional: migration scripts
├── tests/                    # Backend tests
│   ├── conftest.py
│   ├── test_auth.py
│   └── ...
├── requirements.txt
├── run.py
└── wsgi.py
```

---

## 5.4 AI Services (Standalone or in Backend)

```
ai_services/                  # If kept separate
├── skill_assessment/
│   ├── model.py              # Scoring logic
│   └── domain_mapping.py
├── evaluation/
│   ├── code_analyzer.py
│   ├── text_analyzer.py
│   └── plagiarism.py
├── recommender/
│   └── task_ranker.py
└── chatbot/
    ├── rag.py
    └── prompts.py
```

---

## 5.5 Docker

```
docker/
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
└── docker-compose.yml        # Or at root
```

---

## 5.6 Tests

```
tests/
├── e2e/
│   └── student_flow.spec.ts  # Playwright
├── integration/
│   └── api_tests/
└── fixtures/
```

---

# 6. IMPLEMENTATION NOTES (PRACTICAL)

## 6.1 Recommended Libraries

| Category    | Python                             | React/JS             |
| ----------- | ---------------------------------- | -------------------- |
| Auth        | PyJWT, Flask-JWT-Extended, bcrypt  | axios, react-query   |
| Forms       | marshmallow, Pydantic              | React Hook Form, Zod |
| UI          | —                                  | MUI or Chakra UI     |
| Charts      | —                                  | Recharts             |
| File upload | flask-reuploaded, werkzeug         | react-dropzone       |
| Validation  | marshmallow, Cerberus              | Zod                  |
| DB          | PyMongo, (optional) MongoEngine    | —                    |
| Queue       | Celery, Redis                      | —                    |
| NLP         | NLTK, SpaCy, sentence-transformers | —                    |
| ML          | Scikit-learn, (optional) PyTorch   | —                    |

---

## 6.2 API Endpoints (Sample)

### Auth

```
POST   /api/auth/register          { email, password, role, ... }
POST   /api/auth/login             { email, password } → { access_token, refresh_token }
POST   /api/auth/refresh           { refresh_token }
POST   /api/auth/forgot-password   { email }
POST   /api/auth/reset-password    { token, new_password }
```

### Assessment

```
GET    /api/assessment/current     → questions
POST   /api/assessment/submit     { answers } → { domain, score, recommendation }
GET    /api/assessment/result     → last result
```

### Tasks

```
GET    /api/tasks                  ?domain=&difficulty=&page=
GET    /api/tasks/:id
POST   /api/tasks                  (admin) create
PUT    /api/tasks/:id              (admin) update
POST   /api/tasks/:id/claim        (student) claim task
GET    /api/tasks/recommended      (student) AI-recommended list
```

### Submissions

```
POST   /api/submissions            { assignment_id, files, text }
GET    /api/submissions/:id        → submission + ai_feedback + mentor_feedback
```

### Mentor

```
GET    /api/mentor/students        → assigned students
GET    /api/mentor/pending         → pending submissions
POST   /api/mentor/feedback        { submission_id, feedback, approved }
```

### Portfolio

```
GET    /api/portfolio              (student) own portfolio
PUT    /api/portfolio              (student) update visibility/sections
GET    /api/portfolio/export       ?format=pdf|json
```

### Chatbot

```
POST   /api/chatbot/message        { message } → { response }
GET    /api/chatbot/history        → conversation
```

### Admin

```
GET    /api/admin/users            ?role=&status=
POST   /api/admin/users            create user
PUT    /api/admin/users/:id        update user
GET    /api/admin/tasks            all tasks
GET    /api/admin/reports          ?type=&from=&to=
POST   /api/admin/assign-mentor    { student_id, mentor_id }
```

### Client & Projects

```
POST   /api/projects               (client) create project
GET    /api/projects               (client) my projects; (student) assigned
GET    /api/projects/:id/candidates (client) AI-recommended candidates
POST   /api/projects/:id/select    (client) select student(s)
POST   /api/projects/:id/milestones/fund  (client) fund milestone (Escrow)
POST   /api/projects/:id/milestones/:mid/release  (client) release funds
```

### Virtual Workspace

```
GET    /api/workspace/:projectId/messages   → message history
POST   /api/workspace/:projectId/messages   { content }
GET    /api/workspace/:projectId/files      → file list
POST   /api/workspace/:projectId/files      upload file
GET    /api/workspace/:projectId/milestones → milestone status
PUT    /api/workspace/:projectId/milestones/:id  (student) mark progress
```

### Reviews & Reputation

```
POST   /api/reviews               { project_id, reviewee_id, rating, text }
GET    /api/users/:id/reviews     → reputation summary
```

---

## 6.3 RBAC Policy Table

| Resource            | Student  | Client            | Mentor          | Admin      |
| ------------------- | -------- | ----------------- | --------------- | ---------- |
| Own profile         | R, U     | R, U              | R, U            | R, U       |
| Other users         | —        | —                 | R (assigned)    | R, C, U, D |
| Tasks               | R, claim | —                 | R               | R, C, U, D |
| Projects (own)      | R        | R, C, U           | —               | R          |
| Projects (assigned) | R, U     | —                 | —               | R          |
| Own submissions     | R, C     | —                 | —               | R          |
| Others' submissions | —        | —                 | R, U (feedback) | R          |
| Portfolio (own)     | R, U     | —                 | —               | R          |
| Workspace (project) | R, C     | R, C              | —               | R          |
| Escrow/Payment      | —        | R, C, U (release) | —               | R          |
| Chatbot             | R, C     | R, C              | R, C            | R, C       |
| Admin panel         | —        | —                 | —               | Full       |
| Reports             | R (own)  | R (own)           | R (assigned)    | R (all)    |

R=Read, C=Create, U=Update, D=Delete

---

## 6.4 Security Checklist

| Item                | Implementation                                         |
| ------------------- | ------------------------------------------------------ |
| Password hashing    | bcrypt or argon2; never store plain text               |
| JWT                 | Short-lived access (15–30 min); refresh token rotation |
| HTTPS               | Enforce in production                                  |
| CORS                | Whitelist frontend origin; no wildcard in prod         |
| Rate limiting       | 100 req/min per IP for auth; 60/min for API            |
| Input validation    | Validate all inputs; sanitize for XSS                  |
| File upload         | Whitelist extensions; virus scan; size limits          |
| SQL/NoSQL injection | Use parameterized queries; validate ObjectIds          |
| Secrets             | Environment variables; never in code                   |
| Audit logging       | Log auth events, admin actions                         |

---

# Summary

This document provides a complete strategy for building the **AI-Supported Virtual Internship Hub**. Key decisions:

- **Backend:** Flask (or FastAPI) with MongoDB, Celery, Redis
- **Frontend:** React with MUI/Chakra, React Query, React Router
- **AI:** Scikit-learn + NLTK/SpaCy for assessment and evaluation; LLM + RAG for chatbot
- **Storage:** Local files (MVP) → S3/MinIO (production)
- **Phases:** Prototype (FR1 + FR2) → MVP → Beta → Final

**Prototype Scope (Current Phase):**

- **FR1:** User Registration and Authentication — role-based (Student, Mentor, Administrator), login/logout, password validation, RBAC, session handling
- **FR2:** Skill Assessment and Domain Recommendation — MCQ test, automated scoring, display of recommended domains (DigiSkills: Graphic Design, Content Writing, Programming, Freelancing, E-Commerce, QuickBooks, AutoCAD, etc.)
- Frontend and backend must work together with full integration.

Next steps: Set up project structure, implement FR1 (auth) and FR2 (assessment) with complete frontend–backend integration.
