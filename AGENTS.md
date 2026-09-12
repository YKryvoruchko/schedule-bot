# University Schedule System — Project Instructions

## 1. Role

You are the primary senior full-stack engineer and software architect for this repository.

Your job is to IMPLEMENT the requested university schedule system, not merely describe it.

You may create, modify, delete and reorganize project files when necessary.

Do not claim that something is implemented unless the corresponding files and code actually exist and have been validated.

Do not stop after creating a plan. Continue implementation until the current requested milestone is actually complete.

---

# 2. Product

Build a production-oriented university schedule system consisting of:

1. Telegram bot.
2. Responsive web application.
3. FastAPI backend.
4. PostgreSQL database.
5. DOCX schedule importer.
6. Administrative interface.
7. Notification worker.
8. Docker Compose environment.
9. Automated tests.
10. Complete README/documentation.

Telegram bot and website MUST use the same backend and the same PostgreSQL database.

The database is the single source of truth for the schedule.

Never maintain a separate production JSON schedule file.

---

# 3. Critical DOCX Requirement

A real schedule DOCX file may be present in the repository.

Before implementing the final DOCX parser:

1. Locate all .docx files in the repository.
2. Inspect their actual structure.
3. Inspect tables, rows, columns, merged cells, headers, dates, weekdays, lesson numbers, times, teachers, subjects, rooms and links.
4. Determine whether the document contains:

   * multiple groups;
   * odd/even weeks;
   * dates;
   * substitutions;
   * cancelled lessons;
   * different lesson types;
   * merged cells;
   * repeated headers;
   * other special structures.

DO NOT invent a DOCX format.

Adapt the parser to the actual document.

The parser must be isolated behind a clean interface so it can later be adapted to another DOCX format without rewriting the rest of the application.

If the DOCX format is ambiguous, implement a robust normalization layer and produce validation errors instead of silently guessing incorrect data.

---

# 4. Technology

Use:

Backend:

* Python 3.12+
* FastAPI
* SQLAlchemy 2.x
* Alembic
* Pydantic v2
* PostgreSQL
* python-docx

Telegram:

* aiogram 3.x

Frontend:

* Next.js
* TypeScript
* React
* Tailwind CSS
* TanStack Query

Infrastructure:

* Docker
* Docker Compose

Testing:

* pytest
* pytest-asyncio where appropriate

Use current stable package versions compatible with the selected Python/Node versions.

Avoid unnecessary dependencies.

---

# 5. Architecture

Use a modular monolith architecture.

Recommended repository structure:

backend/
bot/
worker/
frontend/
docker-compose.yml
.env.example
.gitignore
README.md
AGENTS.md

Backend structure should separate:

* API routes
* configuration
* database
* ORM models
* Pydantic schemas
* business services
* DOCX parser
* validation
* authentication
* utilities

Do not put the entire backend into one file.

Do not put all Telegram handlers into one file.

Do not put all frontend UI into one component.

Keep responsibilities clearly separated.

---

# 6. Database

Use PostgreSQL.

Use SQLAlchemy 2.x models and Alembic migrations.

At minimum support:

## users

Fields:

* id
* telegram_id
* username
* first_name
* last_name
* notifications_enabled
* notification_minutes_before
* created_at
* updated_at

telegram_id must be unique.

## schedule_versions

Fields:

* id
* filename
* created_at
* is_active

A schedule import must create a new version rather than immediately destroying the previous schedule.

## schedule

Fields should support:

* id
* version_id
* date
* day_of_week
* lesson_number
* starts_at
* ends_at
* subject
* teacher
* meeting_url
* room
* description
* created_at
* updated_at

Use timezone-aware timestamps.

## notification_deliveries

Fields:

* id
* user_id
* schedule_id
* minutes_before
* sent_at

Create a unique constraint preventing duplicate notification delivery for the same:

user + schedule + minutes_before

## schedule_imports

Track:

* filename
* status
* upload time
* processing time
* number of rows
* valid rows
* invalid rows
* warnings
* errors

If the real DOCX demonstrates additional concepts such as groups or odd/even weeks, add appropriate normalized database entities.

Do not force an unsuitable schema merely because it was listed in the initial requirements.

---

# 7. Timezone

Timezone must be configurable.

Use:

TIMEZONE=Europe/Bucharest

as the example default.

Never use naive datetime values in business logic.

Use Python zoneinfo / IANA timezone.

All calculations involving:

* current lesson;
* next lesson;
* countdown;
* notifications;
* today;
* tomorrow;
* current week

must use the configured timezone.

The server timezone must never implicitly determine the university schedule timezone.

---

# 8. Backend API

Implement:

GET /api/schedule/today
GET /api/schedule/tomorrow
GET /api/schedule/week
GET /api/schedule/date/{date}

Admin endpoints:

POST /api/admin/import
GET /api/admin/import/{id}
GET /api/admin/import/{id}/preview
POST /api/admin/import/{id}/confirm

GET /api/admin/schedule
GET /api/admin/versions
POST /api/admin/versions/{id}/activate

Health:

GET /health
GET /health/db

API responses must use Pydantic schemas.

Do not expose raw SQLAlchemy models directly.

---

# 9. Schedule Business Logic

Create a reusable ScheduleService.

It must provide logic for:

* today's schedule;
* tomorrow's schedule;
* current week;
* arbitrary date;
* current lesson;
* next lesson;
* lesson status.

Lesson statuses:

* upcoming
* current
* finished

A lesson is current when:

starts_at <= now < ends_at

A lesson is finished when:

now >= ends_at

The same business logic must be reused by the web frontend and Telegram bot.

Do not duplicate schedule-state calculations independently in multiple applications.

---

# 10. Countdown

The backend is the source of truth for schedule timestamps.

Frontend may update the countdown every second for display.

Do not trust the user's local clock as the authoritative schedule time.

The API should provide timezone-aware timestamps and enough information for the frontend to calculate the remaining duration.

When the lesson ends, the frontend must automatically transition to the next lesson without requiring a page reload.

---

# 11. DOCX Parser

Create a parser interface similar to:

ScheduleParser

and a concrete implementation for DOCX.

The parser pipeline should be:

DOCX
→ extraction
→ normalization
→ parsing
→ validation
→ preview
→ confirmation
→ database import

The parser must produce structured objects rather than directly inserting arbitrary values into the database.

Implement validation for:

* invalid dates;
* invalid weekdays;
* invalid lesson numbers;
* invalid times;
* end before start;
* missing subject;
* malformed meeting URLs;
* suspicious duplicate lessons;
* conflicting lessons.

Do not silently discard unknown data.

Preserve additional information in description when appropriate.

---

# 12. Import Workflow

Uploading a file must NOT immediately replace the active schedule.

Workflow:

1. Upload DOCX.
2. Create import record.
3. Parse file.
4. Validate parsed lessons.
5. Produce preview.
6. Show:

   * total rows;
   * valid rows;
   * warnings;
   * errors.
7. Administrator explicitly confirms.
8. Create a new schedule version.
9. Insert validated schedule.
10. Activate the new version atomically.

If import fails, the currently active schedule must remain untouched.

If the application crashes during import, the previous active schedule must remain usable.

---

# 13. Telegram Bot

Use aiogram 3.x.

Main menu:

* 📅 Сегодня
* 📅 Завтра
* 📚 Неделя
* 🔔 Настройки уведомлений

/start must register/update the Telegram user.

Today:

Show every lesson with:

* lesson number;
* time;
* subject;
* teacher;
* room if available;
* status;
* meeting button.

Current lesson:

🟢 ИДЕТ СЕЙЧАС

Next:

🟡 СЛЕДУЮЩАЯ ПАРА

Finished:

⚪ Завершена

Meeting link must be an inline button.

Tomorrow must display tomorrow's schedule.

Week must group lessons by weekday.

If there are no lessons:

"Сегодня пар нет 🎉"

"Завтра пар нет."

"На этой неделе занятий нет."

Use inline keyboards where useful.

---

# 14. Notifications

Default:

15 minutes before lesson.

Supported configuration must allow:

5
10
15
30

minutes before.

Architecture should also make it easy to add:

0 minutes

for notification at lesson start.

Create a separate worker.

The worker must periodically find lessons approaching their notification threshold.

Before sending:

1. Check user notification settings.
2. Check notification_deliveries.
3. Send Telegram notification.
4. Record delivery.

Use the database uniqueness constraint to guarantee idempotency.

The system must not send duplicate notifications after a restart.

Do not store pending notifications only in RAM.

---

# 15. Telegram Notification

Format approximately:

🔔 Напоминание

Через 15 минут начинается:

📚 Программирование

⏰ 14:00–15:30

👨‍🏫 Иванов Иван Иванович

Add:

🔗 Подключиться к паре

button when a meeting URL exists.

---

# 16. Web Frontend

Build a modern, simple, responsive interface.

Primary objective:

The user should immediately understand:

1. What lesson is happening now?
2. How much time remains?
3. What lesson is next?
4. Where to connect?

Pages:

/

Today

/tomorrow

/week

/admin

Today page should emphasize the current lesson.

Display:

* subject;
* time;
* teacher;
* room;
* meeting link;
* status.

Current lesson should have a prominent block:

🟢 Сейчас идет пара

Remaining countdown must update every second.

Show:

Начало
Конец
Осталось

When the lesson ends, automatically update to the next lesson.

---

# 17. Responsive Week View

Desktop:

Pн | Вт | Ср | Чт | Пт | Сб | Вс

Mobile:

vertical day sections.

Do not create a visually overloaded UI.

Prioritize readability.

---

# 18. Admin UI

Admin must allow:

* login;
* DOCX upload;
* parsing;
* preview;
* validation results;
* errors;
* warnings;
* confirmation;
* active schedule version;
* previous schedule versions;
* activation of an older version;
* deleting/archive management where appropriate.

Do not allow unauthenticated users to access administrative operations.

---

# 19. Authentication

Do not hardcode secrets.

Use .env.

Example:

DATABASE_URL=
TELEGRAM_BOT_TOKEN=
SECRET_KEY=
ADMIN_USERNAME=
ADMIN_PASSWORD_HASH=
TIMEZONE=Europe/Bucharest

Never commit real credentials.

Admin authentication should use secure HTTP-only cookies/session or another appropriate server-side mechanism.

Do not store plaintext passwords in the repository.

---

# 20. Environment

Create:

.env.example

with every required environment variable documented.

Application must fail with a clear startup error if a required secret/configuration value is missing.

---

# 21. Docker

Create Dockerfiles for:

backend
bot
worker
frontend

Create docker-compose.yml with:

postgres
backend
bot
worker
frontend

Use health checks where appropriate.

Backend must run migrations in a documented way.

Do not make the application depend on manually creating database tables.

---

# 22. Restart Safety

After restarting every container:

* schedule remains available;
* users remain available;
* notification settings remain available;
* active schedule version remains available;
* notification delivery history remains available;
* worker resumes correctly;
* no duplicate notifications are generated.

Do not rely on process memory for persistent application state.

---

# 23. Error Handling

Implement proper error handling.

DOCX errors must return useful administrative messages.

API must return appropriate HTTP status codes.

Telegram API errors must be logged and retried where appropriate.

Database errors must be logged.

Do not expose stack traces or secrets to users.

---

# 24. Logging

Use structured/consistent application logging.

Log important events:

* application startup;
* database connection;
* import started;
* import completed;
* import failed;
* schedule activated;
* notification sent;
* notification failed;
* Telegram API failure.

Never log:

* bot token;
* admin password;
* SECRET_KEY;
* session secrets.

---

# 25. Testing

Create meaningful automated tests.

At minimum test:

* date handling;
* timezone handling;
* current lesson;
* next lesson;
* finished lesson;
* empty schedule;
* DOCX parsing;
* DOCX validation;
* duplicate notification prevention;
* notification timing;
* API endpoints;
* database migrations where practical.

If a real DOCX is available, create parser tests against it.

Do not write fake tests that merely assert that functions exist.

---

# 26. README

Create a complete README containing:

1. Project overview.
2. Architecture.
3. Requirements.
4. Local installation.
5. .env setup.
6. Telegram bot creation.
7. Docker startup.
8. Database migrations.
9. DOCX import.
10. Admin login.
11. Notification worker.
12. Telegram polling/webhook.
13. Tests.
14. Deployment.
15. Production considerations.
16. Troubleshooting.

Commands must be copy-pasteable.

---

# 27. Code Quality

Use:

* type hints;
* clear names;
* small functions;
* dependency injection where appropriate;
* async database access where appropriate;
* proper transaction boundaries.

Do not over-engineer.

Do not introduce microservices unnecessarily.

Do not create abstractions without a real purpose.

Comments should explain WHY, not WHAT.

---

# 28. Security

Never commit secrets.

Validate uploaded files.

Restrict DOCX upload size.

Verify file type where practical.

Protect admin endpoints.

Validate URLs.

Avoid SQL injection by using SQLAlchemy.

Do not expose internal database errors.

Use secure cookies for admin authentication.

---

# 29. Development Process

Before making major changes:

1. Inspect the repository.
2. Read existing AGENTS.md files.
3. Inspect the actual DOCX.
4. Determine existing project state.
5. Create/update architecture only where needed.

Do not overwrite existing working code unnecessarily.

Prefer incremental changes.

After implementation of each milestone:

1. Run formatter/linter if configured.
2. Run tests.
3. Run type checks where configured.
4. Run Docker build when appropriate.
5. Fix failures.
6. Only then continue.

---

# 30. Definition of Done

The project is not considered complete until:

* backend exists;
* frontend exists;
* Telegram bot exists;
* notification worker exists;
* PostgreSQL schema exists;
* migrations work;
* DOCX parser works against the actual provided DOCX;
* admin import workflow works;
* schedule API works;
* Telegram menu works;
* website works;
* countdown works;
* timezone works;
* notifications are idempotent;
* Docker Compose starts the application;
* tests pass;
* README is complete;
* .env.example exists;
* no real secrets are committed.

Do not say "done" if any of these are missing.

---

# 31. Execution Strategy

Work in milestones.

Milestone 1:
Repository inspection + actual DOCX analysis + final data model.

Milestone 2:
Backend + PostgreSQL + migrations.

Milestone 3:
DOCX parser + validation + import preview.

Milestone 4:
Schedule API + business logic.

Milestone 5:
Telegram bot.

Milestone 6:
Notification worker.

Milestone 7:
Next.js frontend.

Milestone 8:
Admin UI.

Milestone 9:
Docker + tests + documentation.

After every milestone, run the relevant tests.

Do not stop at a theoretical plan.

---

# 32. Important

The real DOCX structure has priority over assumptions in this document.

If the actual document contradicts an assumed field or structure:

1. inspect the document;
2. adapt the data model/parser;
3. preserve compatibility with the requested product behavior;
4. document the decision.

Never silently invent schedule data.

Never claim to have inspected a file that you did not actually inspect.

Never claim to have run a test that you did not actually run.

Never claim deployment succeeded unless it was actually verified.

Build the actual application.
