"""
Todo API Application

FastAPI backend with AI chatbot and MCP server integration.
Supports user authentication via JWT and task management via REST API or MCP protocol.

Endpoints:
- /health - Health check
- /api/tasks - Task CRUD operations (REST)
- /api/chat - AI chatbot endpoint
- /mcp - MCP server for tool discovery (Streamable HTTP)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import tasks, tags, chat, chatkit
from app.mcp.server import mcp_lifespan, get_mcp_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events:
    - Startup: Create database tables, initialize MCP server
    - Shutdown: Clean up MCP server resources
    """
    # Startup
    create_db_and_tables()

    # Initialize MCP server with its own lifespan
    async with mcp_lifespan(app):
        yield

    # Shutdown (cleanup happens automatically when context exits)


app = FastAPI(
    title="Todo API",
    description="Todo application backend with AI chatbot and MCP server integration",
    version="3.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routers
app.include_router(tasks.router)
app.include_router(tags.router)
app.include_router(chat.router)
app.include_router(chatkit.router)

# Mount MCP server at /mcp endpoint
# This enables tool discovery via Model Context Protocol (Streamable HTTP transport)
app.mount("/mcp", get_mcp_app())


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "mcp": "enabled"}
