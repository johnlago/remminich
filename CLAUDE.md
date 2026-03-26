# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Remminich is a Django companion app for [Immich](https://immich.app/) (a self-hosted photo management system). It enables collaborative family metadata contributions for historical photo archives — approximate dates, locations, and captions — that Immich doesn't natively support. Think "dating app"-style swipe interface for tagging old family photos.

## Development Commands

```bash
# Setup (requires uv and Python 3.12)
uv venv --python=3.12 && source .venv/bin/activate
uv pip install -r requirements.txt

# Run dev server
python manage.py runserver 0.0.0.0:8000

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Docker
docker build -t remminich:latest .
docker run -p 8001:8001 --env-file .env remminich:latest
```

No test suite or linter is configured.

## Environment

Requires a `.env` file (see `.env-sample`):
- `IMMICH_API_KEY` — API key for your Immich instance
- `IMMICH_URL` — Immich server URL (e.g., `http://immich-server:2283/`)

## Architecture

**Django MTV + Immich API wrapper.** Local SQLite stores users and album references; all photo/asset data lives in Immich and is accessed via REST API.

### Key layers

- **`app/views.py`** — Main request handlers. Album browsing, asset updates, user registration/auth.
- **`immich/ImmichClient.py`** — Singleton REST client wrapping Immich's API (albums, assets, thumbnails, places search). Configured from `.env`.
- **`immich/models.py`** — Pydantic models for Immich API payloads (`BulkUpdateAssetsModel`, `UpdateAlbumModel`, `SearchModel`).
- **`app/components/`** — Django-Unicorn reactive components (AJAX-powered modals for editing captions, dates, locations without a full SPA).
- **`app/models.py`** — `CustomUser` (email-based auth, no username field) and `Album` (UUID-keyed reference to Immich albums).

### Data flow

```
Django Templates → Views/Unicorn Components → ImmichClient → Immich Server REST API
                                             → SQLite (users, album refs)
```

### Reactive UI pattern

Interactive modals use [django-unicorn](https://www.django-unicorn.com/) — Python component classes in `app/components/` paired with templates in `app/templates/unicorn/`. These handle caption editing, batch date offset, and location tagging via AJAX without page reloads.

## Deployment

- **CI/CD**: GitHub Actions builds and pushes Docker image to `ghcr.io/marcrleonard/remminich:latest` on push to `main`.
- **Production**: Ansible playbook in `deploy/` sets up Nginx + Systemd + Gunicorn.
- Designed to run alongside Immich in Docker Compose on the same network.
