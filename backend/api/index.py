"""
Vercel Serverless Function Entry Point

This file creates a simplified FastAPI app for Vercel's Python runtime.
MCP server is disabled in serverless mode due to connection limitations.
"""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment flag for serverless mode
os.environ["VERCEL_SERVERLESS"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import tasks, tags, chat, chatkit

# Create a simplified app for Vercel (no MCP server)
app = FastAPI(
    title="Todo API",
    description="Todo application backend (Vercel Serverless)",
    version="3.0.0",
)

# Initialize database on cold start
try:
    create_db_and_tables()
except Exception as e:
    print(f"Database init warning: {e}")

# Configure CORS
cors_origins = [
    "http://localhost:3000",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    cors_origins.append(frontend_url)
    cors_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Thread-Id", "set-auth-jwt"],
)

# Include routers
app.include_router(tasks.router)
app.include_router(tags.router)
app.include_router(chat.router)
app.include_router(chatkit.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "mode": "serverless"}


@app.get("/")
def root():
    return {"message": "Todo API is running", "docs": "/docs"}


# Vercel handler
handler = app
