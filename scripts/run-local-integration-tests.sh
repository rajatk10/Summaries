#!/usr/bin/env bash
set -Eeuo pipefail

compose_file="compose-integration-test.yaml"

cleanup() {
  docker compose -f "$compose_file" down --volumes --remove-orphans
}

trap cleanup EXIT

docker compose -f "$compose_file" up --detach --wait test-db

#Set up environment variables for production

export ENVIRONMENT=test
export DATABASE_URL="postgresql://summaries_test:summaries_test@127.0.0.1:15433/summaries-test"

#now run and add models to newly setup database

uv run tortoise -c app.config.TORTOISE_ORM migrate
uv run tortoise -c app.config.TORTOISE_ORM history

#Finally running the tests

uv run pytest tests/integration -m integration -v