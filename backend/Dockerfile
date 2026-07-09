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
    fastapi==0.104.1 \
    "uvicorn[standard]==0.23.2" \
    sqlalchemy==2.0.23 \
    aiosqlite==0.19.0 \
    "passlib[bcrypt]==1.7.4" \
    "python-jose[cryptography]==3.3.0" \
    python-multipart==0.0.6 \
    pydantic==2.5.2 \
    pydantic-settings==2.1.0 \
    chess==1.10.0 \
    torch==2.1.2 \
    numpy==1.26.2 \
    tqdm==4.66.1

# Copy the entire project context (since backend and worker depend on root modules like 'engine' and 'analysis')
COPY . /app/

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
