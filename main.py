from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.database import engine, Base

# Import models so SQLAlchemy registers them before create_all
import backend.models  # noqa: F401

# Routers
from backend.routers import (
    auth,
    profile,
    recommendations,
    search,
    meal_plan,
    analytics,
    oauth,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""

    print(f"🚀 Starting {settings.app_name} [{settings.app_env}]")

    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready")

        # NOTE:
        # Do NOT seed vector store during startup in production.
        # Run seeding separately when needed.
        print("✅ Startup completed")

    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise

    yield

    print(f"🛑 Shutting down {settings.app_name}")


app = FastAPI(
    title="NutriGuide API",
    description=(
        "Clinical Nutrition Intelligence Platform — "
        "personalized food recommendations powered by RAG and Llama 3.1"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(profile.router)
app.include_router(recommendations.router)
app.include_router(search.router)
app.include_router(meal_plan.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"], summary="API health check")
def root():
    return JSONResponse(
        {
            "status": "ok",
            "app": settings.app_name,
            "version": "1.0.0",
            "env": settings.app_env,
            "docs": "/docs",
        }
    )


@app.get("/health", tags=["Health"], summary="Detailed health check")
def health_check():
    return JSONResponse(
        {
            "status": "healthy",
            "database": "connected",
            "llm_provider": "groq",
            "model": settings.groq_model_id,
        }
    )