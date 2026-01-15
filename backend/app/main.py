from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import app_logger
from app.api import auth, procedures, chat, vision, tips, executions, startup
from app.api import router as nextgen_router
from app.api import command_center
from app.api import import_pipeline
from app.api import dashboard_stats
from app.api import cloud_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    app_logger.info("Démarrage des services Command Center...")
    
    from app.services.idle_manager import get_idle_manager
    from app.services.resource_throttler import get_resource_throttler
    from app.services.smart_rag_service import get_smart_rag_service
    
    idle_manager = get_idle_manager()
    throttler = get_resource_throttler()
    rag_service = get_smart_rag_service()
    
    await idle_manager.start()
    await throttler.start()
    await rag_service.start()
    
    app_logger.info("Services Command Center démarrés")
    
    yield
    
    # Shutdown
    app_logger.info("Arrêt des services Command Center...")
    await idle_manager.stop()
    await throttler.stop()
    await rag_service.stop()
    app_logger.info("Services Command Center arrêtés")

# Créer les tables
Base.metadata.create_all(bind=engine)
app_logger.info("Tables de base de données créées/vérifiées")

# Créer le répertoire d'uploads
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app_logger.info(f"Répertoire d'uploads créé/vérifié: {settings.UPLOAD_DIR}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Logger le démarrage
app_logger.info("Application FastAPI initialisée", {"title": settings.PROJECT_NAME})

# Servir les fichiers statiques (uploads)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(procedures.router, prefix=f"{settings.API_V1_STR}/procedures", tags=["procedures"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(vision.router, prefix=f"{settings.API_V1_STR}/vision", tags=["vision"])
app.include_router(tips.router, prefix=f"{settings.API_V1_STR}/tips", tags=["tips"])
app.include_router(executions.router, prefix=f"{settings.API_V1_STR}/executions", tags=["executions"])
app.include_router(startup.router, prefix=f"{settings.API_V1_STR}/startup", tags=["startup"])

# Next-Gen Dashboard Routes
app.include_router(nextgen_router.router, tags=["Next-Gen"])

# Command Center Routes
app.include_router(command_center.router, tags=["Command Center"])

# Import Pipeline Routes
app.include_router(import_pipeline.router, tags=["Import Pipeline"])

# Dashboard Stats Routes (public, sans auth)
app.include_router(dashboard_stats.router, prefix="/api", tags=["Dashboard Stats"])

# Cloud Data Routes (Vercel/Supabase)
app.include_router(cloud_data.router, prefix="/api", tags=["Cloud Data"])


@app.get("/")
async def root():
    return {"message": "Procédures Maintenance Photovoltaïque API"}


@app.get("/health")
async def health():
    return {"status": "ok"}
