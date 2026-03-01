# AlumniConnect Backend

FastAPI + PostgreSQL backend for the AlumniConnect platform.

---

## Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 |
| Password Hashing | passlib + bcrypt |
| DB Admin UI | pgAdmin |
| Container | Docker Compose |

---

## Quick Start

### 1. Clone / place the project
```bash
cd alumniconnect-backend
```

### 2. Start all containers
```bash
docker compose up --build -d
```

This starts three containers:
- **db** — PostgreSQL on port 5432
- **api** — FastAPI on port 8000 (auto-reload enabled)
- **pgadmin** — pgAdmin UI on port 5050

### 3. Wait ~10 seconds for Postgres to initialize, then seed the database
```bash
docker compose exec api python seed.py
```

This populates:
- All role categories, target roles, skills, and todo items
- A default admin account
- 2 sample student accounts
- 2 sample alumni accounts

### 4. Open the API docs
```
http://localhost:8000/docs
```

Interactive Swagger UI — you can test every endpoint here.

### 5. Open pgAdmin (optional)
```
http://localhost:5050
Email:    admin@alumni.com
Password: admin
```

Connect to server:
- Host: `db`
- Port: `5432`
- Username: `alumniuser`
- Password: `alumnipass`
- Database: `alumniconnect`

---

## Login Credentials (after seeding)

| Role | Email | Password |
|---|---|---|
| Admin | admin@alumni.com | admin123 |
| Student | arjun@college.edu | student123 |
| Student | priya@college.edu | student123 |
| Alumni | karthik@alumni.edu | alumni123 |
| Alumni | sneha@alumni.edu | alumni123 |

---

## Authentication

Login is the **only** endpoint that checks credentials. Every other endpoint is open — no token required. The frontend is responsible for routing users to the right dashboard after login.

**POST /auth/login**
```json
{ "email": "arjun@college.edu", "password": "student123" }
```
Returns the user object with `id`, `name`, `email`, `role`, `readiness_score`, etc.

---

## API Endpoints

### Auth
| Method | Route | Description |
|---|---|---|
| POST | /auth/login | Validate credentials, returns user object |

### Students
| Method | Route | Description |
|---|---|---|
| POST | /students/register | Register a new student |
| GET | /students/{id} | Get full student profile |
| PATCH | /students/{id} | Update profile fields (name, dept, linkedin, github, target_role) |
| PUT | /students/{id}/skills | Replace all skills (send array of skill_ids) |
| GET | /students/{id}/projects | List projects |
| POST | /students/{id}/projects | Add project |
| PATCH | /students/{id}/projects/{pid} | Update project |
| DELETE | /students/{id}/projects/{pid} | Delete project |
| POST | /students/{id}/certifications | Add cert |
| PATCH | /students/{id}/certifications/{cid} | Update cert |
| DELETE | /students/{id}/certifications/{cid} | Delete cert |
| POST | /students/{id}/experiences | Add experience |
| PATCH | /students/{id}/experiences/{eid} | Update experience |
| DELETE | /students/{id}/experiences/{eid} | Delete experience |
| GET | /students/{id}/readiness | Get readiness score + level |
| GET | /students/{id}/roadmap | Get todo list for current level and target role |
| GET | /students/{id}/mentors | Get top 5 suggested alumni mentors |
| GET | /students/{id}/jobs | Browse approved jobs (filtered by readiness score) |
| GET | /students/{id}/questions | List all questions the student has asked |

### Alumni
| Method | Route | Description |
|---|---|---|
| GET | /alumni/ | List all alumni |
| GET | /alumni/{id} | Get alumni public profile |
| POST | /alumni/{id}/profile-updates | Submit profile update for admin approval |
| GET | /alumni/{id}/profile-updates | Get my submitted updates and their status |
| POST | /alumni/{id}/jobs | Post a job/internship (goes to pending) |
| GET | /alumni/{id}/jobs | List my job postings |
| DELETE | /alumni/{id}/jobs/{jid} | Delete a job posting |
| GET | /alumni/{id}/questions | Inbox of questions (anonymous — no student_id) |
| POST | /alumni/{id}/questions/{qid}/answer | Answer a question |
| PATCH | /alumni/{id}/questions/{qid}/answer | Edit an existing answer |

### Q&A
| Method | Route | Description |
|---|---|---|
| POST | /questions/ | Ask a question (body: student_id, alumni_id, question) |
| GET | /questions/alumni/{alumni_id} | Public Q&A thread for an alumni |

### Jobs
| Method | Route | Description |
|---|---|---|
| GET | /jobs/ | List all approved jobs |
| GET | /jobs/{id} | Get job detail |
| POST | /jobs/{id}/apply?student_id= | Apply to a job |
| GET | /jobs/{id}/applications | List all applicants for a job |

### Admin
| Method | Route | Description |
|---|---|---|
| GET | /admin/stats | Dashboard stats (user counts, pending counts) |
| GET | /admin/users?role= | List all users, optional role filter |
| POST | /admin/users | Create any user (any role) |
| DELETE | /admin/users/{id} | Delete a user |
| POST | /admin/transition-to-alumni | Transition a student to alumni |
| GET | /admin/profile-updates?status= | List profile update requests |
| POST | /admin/profile-updates/{id}/action | Approve or reject a profile update |
| GET | /admin/job-postings?status= | List job postings |
| POST | /admin/job-postings/{id}/action | Approve or reject a job posting |
| GET | /admin/qa | Full Q&A list with student identities visible |

### Reference Data (taxonomy)
| Method | Route | Description |
|---|---|---|
| GET | /reference/categories | List role categories |
| GET | /reference/target-roles?category_id= | List target roles |
| GET | /reference/skills?category_id= | List skills (fixed list) |
| GET | /reference/todos?category_id=&level= | List todo items |
| POST | /reference/categories | Create a category |
| POST | /reference/target-roles | Create a target role |
| POST | /reference/skills | Add a skill to the fixed list |
| POST | /reference/todos | Add a todo item |

---

## Readiness Scoring Rules ("AI Career Analyzer")

| Category | Points |
|---|---|
| LinkedIn URL | +3 |
| GitHub URL | +3 |
| Target role set | +4 |
| Skills (×2 each, cap 10 skills) | max 20 |
| Skill matches target role keywords (×1 each, cap 10) | max 10 |
| Projects (×5 each, cap 4) | max 20 |
| Project has description (×1, cap 4) | max 4 |
| Project has GitHub URL (×1, cap 4) | max 4 |
| Project has tech stack tagged (×0.5, cap 4) | max 2 |
| Certifications (×7.5 each, cap 2) | max 15 |
| Internship experience | +15 |
| Freelance or part-time (if no internship) | +8 |

**Total: 100 points**

| Score | Level |
|---|---|
| 0–24 | Foundation |
| 25–49 | Skill Building |
| 50–74 | Internship Ready |
| 75–100 | Interview Ready |

Score is recomputed automatically every time the student updates their profile, skills, projects, certs, or experience.

---

## Project Structure

```
alumniconnect-backend/
├── app/
│   ├── main.py              ← FastAPI app + router registration + table creation
│   ├── database.py          ← SQLAlchemy engine + session + Base
│   ├── models/
│   │   └── models.py        ← All SQLAlchemy table definitions
│   ├── schemas/
│   │   └── schemas.py       ← All Pydantic request/response models
│   ├── routers/
│   │   ├── auth.py          ← Login
│   │   ├── student.py       ← Student dashboard endpoints
│   │   ├── alumni.py        ← Alumni dashboard endpoints
│   │   ├── admin.py         ← Admin dashboard endpoints
│   │   ├── qa.py            ← Public Q&A thread
│   │   ├── jobs.py          ← Job browsing and applications
│   │   └── reference.py     ← Skills, roles, categories, todos
│   └── services/
│       ├── scoring.py       ← Readiness score computation
│       ├── matching.py      ← Mentor suggestion engine
│       └── roadmap.py       ← Todo list generation
├── seed.py                  ← Seed script (run once)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```
