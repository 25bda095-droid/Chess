FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install pip requirements if provided
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Explicitly install packages needed for backend and worker
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    aiosqlite \
    "passlib[bcrypt]" \
    "python-jose[cryptography]" \
    python-multipart \
    pydantic \
    pydantic-settings \
    chess \
    torch \
    numpy \
    tqdm

# Copy the entire project context (since backend and worker depend on root modules like 'engine' and 'analysis')
COPY . /app/

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
