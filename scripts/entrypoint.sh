#!/bin/sh
# A entrypoint docker script to wire the tortoise ORM load when newer instances are loaded.
set -e

echo "Running Tortoise ORM migrations..."
# Execute your migration command before starting the server
tortoise -c app.config.TORTOISE_ORM migrate

echo "Starting FastAPI server..."
exec "$@"
