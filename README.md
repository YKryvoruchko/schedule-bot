# University Schedule System

Production-oriented university schedule system with a FastAPI backend, PostgreSQL database, DOCX import workflow, Telegram bot, notification worker, Next.js frontend, Docker Compose and tests.

## DOCX Findings

The repository contains one real schedule file: `schedule.docx`. It has two Word tables with merged cells. The document is a weekly recurring grid, not a dated list. It contains groups `РЗ-251`, `РЗ-252`, `РЗ-253`, weekdays Monday-Friday, lesson numbers 1-4, week ranges such as `1-15`, odd/even markers `н/пар.` and `пар.`, lesson types such as `лекція`, `лаб.`, `практика`, teachers and meeting links. It does not contain explicit calendar dates, explicit lesson times, substitutions, cancellations or rooms.

Because dates are absent, imported rows are stored as recurring schedule entries. API responses derive concrete dates from `SEMESTER_START_DATE` and `TIMEZONE`. Default lesson times are documented in the parser and can be adjusted in code if the university provides official times.

## Architecture

- `backend/`: FastAPI, SQLAlchemy 2.x, Alembic, DOCX parser, admin import workflow, schedule API.
- `bot/`: aiogram polling bot using the same backend and database.
- `worker/`: notification worker using DB uniqueness for idempotency.
- `frontend/`: Next.js app with today, tomorrow, week and admin pages.
- `docker-compose.yml`: PostgreSQL, backend, bot, worker and frontend.

## Local Setup

```bash
cp .env.example .env
cd backend
python -m pip install -e .[test]
python -c "from app.core.security import hash_password; print(hash_password('admin-password'))"
```

Put the generated hash into `ADMIN_PASSWORD_HASH` in `.env`.

## Telegram Bot

Create a bot with BotFather, copy the token into `TELEGRAM_BOT_TOKEN`, then run the `bot` service. `/start` registers or updates the Telegram user in the backend database.

## Docker Startup

```bash
docker compose up --build
```

Backend: `http://localhost:8000`  
Frontend: `http://localhost:3000`

The backend container runs `alembic upgrade head` before starting.

## DOCX Import

1. Open `http://localhost:3000/admin`.
2. Log in with `ADMIN_USERNAME` and the password whose hash is in `.env`.
3. Upload a `.docx` schedule.
4. Review row counts, warnings, errors and preview.
5. Confirm the import to create and activate a new schedule version atomically.

Failed imports do not replace the active schedule.

## API

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/api/schedule/today?group=РЗ-252"
curl "http://localhost:8000/api/schedule/tomorrow?group=РЗ-252"
curl "http://localhost:8000/api/schedule/week?group=РЗ-252"
curl http://localhost:8000/api/schedule/date/2026-09-15
```

## Tests

```bash
cd backend
pytest
```

## Production Notes

Use a real random `SECRET_KEY`, a strong admin password hash, a managed PostgreSQL instance or persistent Docker volume, HTTPS and secure cookies. Keep `.env` out of git. The notification worker records each delivery with a unique `user + schedule + minutes_before` constraint, so restarts do not duplicate sent reminders.

## Troubleshooting

- `401` in admin: regenerate `ADMIN_PASSWORD_HASH` and restart backend.
- Empty schedule: import and confirm a DOCX version, then request a date whose week number matches the imported week ranges.
- Wrong odd/even lessons: verify `SEMESTER_START_DATE`.
- Telegram errors: check `TELEGRAM_BOT_TOKEN` and backend reachability from the bot container.
