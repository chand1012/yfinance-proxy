from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


app.include_router(ticker.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "YFinance Proxy API"}


mcp = FastMCP.from_fastapi(app=app, name="yfinance mcp")
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

# @app.get("/health", tags=["health"])
# def health_check():
#     return {"status": "healthy"}
