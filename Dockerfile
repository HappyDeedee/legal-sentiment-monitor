FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    UV_PYTHON=3.11 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    MONITOR_HOST=0.0.0.0 \
    MONITOR_PORT=8080 \
    MONITOR_DATA_DIR=/app/monitor_data \
    MONITOR_BROWSER_DATA_DIR=/app/browser_data \
    MONITOR_ACCOUNT_PROFILE_ROOT=/app/monitor_data/account_profiles \
    MONITOR_LOGIN_QR_HEADLESS=true \
    MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false \
    MONITOR_CRAWLER_HEADLESS=true \
    MONITOR_CDP_CONNECT_EXISTING=false

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gnupg libgl1 libglib2.0-0 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --default-timeout=120 --retries=10 -i https://pypi.tuna.tsinghua.edu.cn/simple uv==0.11.23

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --python 3.11

COPY . .

RUN mkdir -p /app/monitor_data /app/browser_data \
    && chmod -R 777 /app/monitor_data /app/browser_data

EXPOSE 8080

CMD ["sh", "-c", "uv run uvicorn api.main:app --host ${MONITOR_HOST:-0.0.0.0} --port ${MONITOR_PORT:-8080}"]
