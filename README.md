# LinkFlowAnalytics – URL Shortener with Analytics

LinkFlowAnalytics is a production-ready URL shortening service with built-in click analytics.  
It generates 5‑character short links, tracks every redirect, and provides detailed statistics per day and user agent.  
Built with modern Python practices – fully typed, tested, and containerized.

---

## Killer Features

- **Link Shortening** – Generate unique short URLs (5 chars, alphanumeric) instantly.
- **Click Analytics** – Collect and analyze traffic: daily breakdowns, user agents, and more.
- **Security & Isolation** – JWT authentication ensures each user sees only their own data.
- **Performance Optimized** – Background tasks buffer clicks, Redis caches popular links for fast redirects.
- **Quality First** – 85% test coverage, type hints, SOLID principles, and clean architecture.

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Pydantic](https://img.shields.io/badge/Pydantic-2.0-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-alpine?logo=redis)
![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)
![Pytest](https://img.shields.io/badge/Pytest-8.x-yellow?logo=pytest)
![Alembic](https://img.shields.io/badge/Alembic-✓-lightgrey)

---

## Quick Start

### Prerequisites
- [Git](https://git-scm.com/)
- [Docker](https://docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

### Steps

```bash
# 1. clone this repository:
git clone https://github.com/meteoradev/LinkFlowAnalytics
cd LinkFlowAnalytics


# 2. setup .env file:
cp .env.example . env
# edit .env file with ur data


# 3. run the project
docker compose up -d


# 4. after all, delete created network and containers.
docker compose down
```

### After startup, the API will be available at:

Main API: http://localhost:8000

Interactive Swagger docs: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc


## API endpoints
POST /users/ - create a user, does not require authentication.  
POST /token/ - authenticate and obtain a JWT token, does not require authentication.  
POST /links/ - create a short link, requires authentication.  
GET /{short_url} - redirect via the short link, does not require authentication.  
GET /analytics/summary/ - get analytics for all your links as a basic user, requires authentication.  
GET /analytics/premium/summary - get analytics for all your links as a premium user, requires authentication.  
GET /analytics/{short_url} - get analytics for one of your link {short_url} as a basic user, requires authentication.  
GET /analytics/premium/{short_url} - get analytics for one of your link {short_url} as a premium user, requires authentication.  
PUT /users/{user_id} - update user with id {user_id}, requires authentication.  
PATCH /users/{user_id} - partially update user with id {user_id}, requires authentication.  
DELETE /users/{user_id} - delete user with id {user_id}, requires authentication.  
DELETE /links/{short_url} - delete link {short_url}, requires authentication.  

**All endpoints that require authentication expect a valid JWT token in the Authorization: Bearer <token> header.**

## Running Tests

Tests are written with Pytest and run inside an isolated Docker environment:
```bash
docker compose up tests
````

Test coverage is currently 85% and includes unit, integration, and end‑to‑end scenarios.
## Database Migrations

Migrations are managed with Alembic. To create or apply migrations:
```bash

# Create a new migration (autogenerate)
docker compose exec api alembic revision --autogenerate -m "Describe your changes"

# Apply pending migrations
docker compose exec api alembic upgrade head

```
