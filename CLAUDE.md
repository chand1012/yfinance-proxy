# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

yfinance-proxy is a FastAPI-based proxy service for the yfinance library. It exposes Yahoo Finance data via HTTP endpoints under `/{symbol}/`.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the development server (with auto-reload)
uv run fastapi dev main.py

# Run production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Build and run with Docker
docker compose up --build

# Run Docker in detached mode
docker compose up -d --build
```

## Architecture

```
app/
├── main.py              # FastAPI app setup, middleware, exception handlers
├── models/              # Pydantic request/response models
│   └── ticker.py        # Models for all ticker-related endpoints
├── routes/              # API route handlers
│   └── ticker.py        # /api/v1/ticker/* endpoints
└── services/            # Business logic layer
    └── yfinance_service.py  # yfinance wrapper with data transformation
```

## API Endpoints

- `GET /health` - Health check
- `GET /{symbol}` - Full ticker info
- `GET /{symbol}/quote` - Current market quote
- `GET /{symbol}/history` - Historical OHLCV data (supports period, interval, date range)
- `GET /{symbol}/recommendations` - Analyst recommendations
- `GET /{symbol}/actions` - Dividends and splits
- `GET /{symbol}/news` - Related news articles
- `GET /{symbol}/financials` - Income statement, balance sheet, cash flow
- `GET /{symbol}/holders` - Institutional and mutual fund holders
- `GET /{symbol}/options` - Options chain data

OpenAPI docs available at `/docs` when server is running.
