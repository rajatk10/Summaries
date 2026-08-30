# FastAPI TDD summaries service
An asynchronous API that fetches, stores, and generates extractive summaries for publicly accessible articles.

Built with FastAPI, PostgreSQL, Tortoise ORM, Trafilatura, and NLTK, and packaged/distributed as a Docker image.

## Tech stack
Python · FastAPI · PostgreSQL · Tortoise ORM · Trafilatura · NLTK · Docker

## Caveats
- Only publicly accessible, unauthenticated article URLs are supported.
- This is a learning project and URL fetching is not yet hardened for production use.