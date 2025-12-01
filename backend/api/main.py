from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.core.config import settings
from backend.core.logger import logger
from backend.core.database import init_db, close_db

from .score_router import router as score_router
from .customers import router as customers_router
from .alerts import router as alerts_router
from backend.api.train_router import router as train_router
from backend.api.model_compare import router as compare_router
from backend.api.rollback_router import router as rollback_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Early Risk Signals API")
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
    
    # Print routing table
    if settings.DEBUG:
        from fastapi.routing import APIRoute
        print("\n" + "="*60)
        print("REGISTERED ROUTES:")
        print("="*60)
        for route in app.routes:
            if isinstance(route, APIRoute):
                methods = ",".join(route.methods)
                print(f"{methods:8} {route.path}")
        print("="*60 + "\n")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Early Risk Signals API")
    await close_db()


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(score_router, prefix="/score", tags=["scoring"])
app.include_router(customers_router, prefix="/customer", tags=["customers"])
app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
app.include_router(train_router, prefix="/train", tags=["training"])
app.include_router(compare_router, prefix="/train/compare", tags=["training"])
app.include_router(rollback_router, prefix="/train", tags=["training"])


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Early Risk Signals API",
        "version": settings.API_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled"
    }
