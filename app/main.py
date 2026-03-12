from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.routes import ticker


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="YFinance Proxy API",
    description="A proxy API for accessing Yahoo Finance data via yfinance",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


# Mount static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/", tags=["health"], response_class=HTMLResponse)
def root():
    """Serve the frontend HTML page."""
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>YFinance Proxy API</h1><p>Frontend not available.</p>", status_code=404)


app.include_router(ticker.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}


mcp = FastMCP.from_fastapi(app=app, name="yfinance mcp", stateless_http=True)
mcp_app = mcp.http_app(path="/mcp")

combined_app = FastAPI(
    title="E-commerce API with MCP",
    routes=[
        *mcp_app.routes,  # MCP routes
        *app.routes,  # Original API routes
    ],
    lifespan=mcp_app.lifespan,
)

combined_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
