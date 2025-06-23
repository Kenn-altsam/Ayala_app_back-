from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.exceptions import AppException
from src.core.cache import init_redis, close_redis
from src.companies.router import router as companies_router
from src.auth.router import router as auth_router
from src.funds.router import router as funds_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Application starting up...")
    # Redis disabled for now
    # await init_redis()
    yield
    # Shutdown
    print("🔄 Application shutting down...")
    # await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    Ayala Foundation API for discovering and matching companies with charity funds.
    Provides location-based company search and AI-powered matching capabilities.
    """,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(companies_router, prefix="/api/v1", tags=["Companies"])
app.include_router(funds_router, prefix="/api/v1", tags=["Funds"])


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "error_code": exc.error_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation error",
            "errors": exc.errors()
        }
    )

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "success",
        "message": "Service is healthy",
        "version": settings.VERSION
    } 