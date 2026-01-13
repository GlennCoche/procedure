from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import app_logger
from app.api import auth, procedures, chat, vision, tips, executions, startup

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
app.include_router(procedures.router, prefix=settings.API_V1_STR, tags=["procedures"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(vision.router, prefix=settings.API_V1_STR, tags=["vision"])
app.include_router(tips.router, prefix=settings.API_V1_STR, tags=["tips"])
app.include_router(executions.router, prefix=f"{settings.API_V1_STR}/executions", tags=["executions"])
app.include_router(startup.router, prefix=f"{settings.API_V1_STR}/startup", tags=["startup"])


@app.get("/")
async def root():
    return {"message": "Procédures Maintenance Photovoltaïque API"}


@app.get("/health")
async def health():
    return {"status": "ok"}
