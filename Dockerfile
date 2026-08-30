# Refer docker multi stage build and segregate the build and runtime

#UV Params
ARG UV_VERSION=0.12.1
FROM astral/uv:${UV_VERSION} AS uv

#Builder
FROM python:3.14-slim AS builder
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

RUN /app/.venv/bin/python -m nltk.downloader -d /opt/nltk_data punkt punkt_tab stopwords

# Runner

FROM python:3.14-slim AS runtime

ENV PATH="/app/.venv/bin:${PATH}" NLTK_DATA=/opt/nltk_data PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app

WORKDIR /app

RUN mkdir -p /app/logs && chown -R app:app /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /opt/nltk_data /opt/nltk_data
COPY --chown=app:app app ./app

COPY scripts/entrypoint.sh /
RUN chmod +x /entrypoint.sh

USER app

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

