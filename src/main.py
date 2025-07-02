"""
Ayala Foundation Backend API

Main FastAPI application entry point for the Ayala Foundation backend.
This service helps charity funds discover companies and sponsorship opportunities.
"""

import os
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .ai_conversation.router import router as ai_conversation_router
from .companies.router import router as companies_router
from .auth.router import router as auth_router
from .funds.router import router as funds_router
from .core.config import get_settings
from .core.database import init_database

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    print("✅ Ayala Foundation Backend API starting up")
    # Initialize database tables
    init_database()
    print("✅ Database initialized")
    yield
    print("✅ Ayala Foundation Backend API shutting down")

# Create FastAPI app
app = FastAPI(
    title="Ayala Foundation Backend API",
    description="Backend service for charity funds to discover companies and sponsorship opportunities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
origins = settings.allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Main endpoints:
# - /api/v1/auth/* - Authentication endpoints
# - /api/v1/funds/* - Fund profile management and main chat endpoint
# - /api/v1/ai/* - Advanced AI assistant endpoints
# - /api/v1/companies/* - Company search and data endpoints
app.include_router(auth_router, prefix="/api/v1")
app.include_router(funds_router, prefix="/api/v1")
app.include_router(ai_conversation_router, prefix="/api/v1")
app.include_router(companies_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "success",
        "message": "Ayala Foundation Backend API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "success",
        "message": "API is healthy",
        "data": {
            "service": "ayala-foundation-backend",
            "version": "1.0.0"
        }
    } 