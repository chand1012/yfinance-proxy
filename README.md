# yfinance-proxy

A FastAPI-based proxy service for accessing Yahoo Finance data via HTTP.

## Quick Start

### Using Docker (recommended)

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Local Development

```bash
# Install dependencies
uv sync

# Run development server with auto-reload
uv run fastapi dev main.py
```

## API Usage

```bash
# Get full ticker info
curl http://localhost:8000/AAPL

# Get current quote
curl http://localhost:8000/AAPL/quote

# Get historical data
curl "http://localhost:8000/AAPL/history?period=1mo&interval=1d"

# Get with date range
curl "http://localhost:8000/AAPL/history?start=2024-01-01&end=2024-06-01"

# Get analyst recommendations
curl http://localhost:8000/AAPL/recommendations

# Get dividends and splits
curl http://localhost:8000/AAPL/actions

# Get news
curl http://localhost:8000/AAPL/news

# Get financial statements
curl http://localhost:8000/AAPL/financials
curl "http://localhost:8000/AAPL/financials?quarterly=true"

# Get holder information
curl http://localhost:8000/AAPL/holders

# Get options chain
curl http://localhost:8000/AAPL/options
curl "http://localhost:8000/AAPL/options?date=2024-12-20"
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
