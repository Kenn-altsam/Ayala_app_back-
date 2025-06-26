"""
Ayala Foundation Backend API

Main FastAPI application entry point for the Ayala Foundation backend.
This service helps charity funds discover companies and sponsorship opportunities.
"""

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .ai_conversation.router import router as ai_conversation_router
from .core.config import get_settings

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Ayala Foundation Backend API",
    description="Backend service for charity funds to discover companies and sponsorship opportunities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(ai_conversation_router, prefix="/api/v1")

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