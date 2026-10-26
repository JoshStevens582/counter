FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY pages ./pages
RUN uv sync --frozen --no-dev

RUN useradd --system --uid 10001 --home-dir /app counter \
    && mkdir -p /app/data \
    && chown -R counter:counter /app/data
USER counter

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8788

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8788/api/ready')"

CMD ["uvicorn", "counter.main:app", "--host", "0.0.0.0", "--port", "8788", "--app-dir", "src", "--proxy-headers", "--forwarded-allow-ips", "*"]
