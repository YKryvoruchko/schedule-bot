FROM python:3.12-slim
WORKDIR /app
COPY worker/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir .
COPY backend ./backend
COPY worker/worker_app ./worker_app
ENV PYTHONPATH=/app/backend
CMD ["python", "-m", "worker_app.main"]
