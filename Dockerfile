FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Étape 1 : installer uniquement les dépendances (layer caché tant que pyproject/uv.lock ne changent pas)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Étape 2 : copier le code source et installer le projet lui-même
COPY . .
RUN uv sync --frozen --no-dev
