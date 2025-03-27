# =========
# Stage: builder
# =========
FROM python:3.11-slim AS builder
WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip setuptools poetry \
    --timeout 60 \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple/ && \
    poetry config virtualenvs.create false

ARG MODE=prod

RUN if [ "$MODE" = "test" ]; then \
      poetry install --with dev --no-interaction --no-ansi; \
    else \
      poetry install --without dev --no-interaction --no-ansi; \
    fi

COPY . .

# =========
# Stage: production
# =========
FROM python:3.11-slim AS production
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--log-level", "info"]

# =========
# Stage: testing
# =========
FROM python:3.11-slim AS testing
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/pytest /usr/local/bin/pytest

CMD ["pytest", "-v"]