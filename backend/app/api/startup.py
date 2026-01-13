from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import subprocess
import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional

router = APIRouter()

# État global des processus
backend_process: Optional[subprocess.Popen] = None
frontend_process: Optional[subprocess.Popen] = None

def check_backend_running() -> bool:
    """Vérifier si le backend est en cours d'exécution"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_frontend_running() -> bool:
    """Vérifier si le frontend est en cours d'exécution"""
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=2)
        return response.status_code == 200
    except:
        return False

@router.get("/status")
async def get_status():
    """Obtenir l'état des serveurs"""
    return {
        "backend": {
            "running": check_backend_running(),
            "url": "http://localhost:8000"
        },
        "frontend": {
            "running": check_frontend_running(),
            "url": "http://localhost:3000"
        }
    }

@router.post("/start")
async def start_servers():
    """Démarrer les serveurs"""
    global backend_process, frontend_process
    
    # Vérifier si déjà en cours d'exécution
    if check_backend_running() and check_frontend_running():
        return {
            "status": "already_running",
            "message": "Les serveurs sont déjà en cours d'exécution"
        }
    
    # Démarrer le backend si nécessaire
    if not check_backend_running():
        backend_dir = Path(__file__).parent.parent.parent
        venv_python = backend_dir / "venv" / "bin" / "python"
        
        if not venv_python.exists():
            return {
                "status": "error",
                "message": "Environnement virtuel non trouvé. Exécutez d'abord: cd backend && python3 -m venv venv"
            }
        
        # Démarrer uvicorn
        backend_process = subprocess.Popen(
            [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Démarrer le frontend si nécessaire
    if not check_frontend_running():
        frontend_dir = Path(__file__).parent.parent.parent.parent / "frontend"
        
        if not (frontend_dir / "node_modules").exists():
            return {
                "status": "error",
                "message": "Dépendances npm non installées. Exécutez d'abord: cd frontend && npm install"
            }
        
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    return {
        "status": "starting",
        "message": "Démarrage des serveurs en cours..."
    }

@router.post("/stop")
async def stop_servers():
    """Arrêter les serveurs"""
    global backend_process, frontend_process
    
    # Arrêter les processus
    if backend_process:
        backend_process.terminate()
        backend_process = None
    
    if frontend_process:
        frontend_process.terminate()
        frontend_process = None
    
    return {
        "status": "stopped",
        "message": "Serveurs arrêtés"
    }

@router.get("/logs")
async def get_logs():
    """Stream des logs en temps réel"""
    import asyncio
    async def generate():
        # Pour l'instant, on retourne l'état
        # Dans une vraie implémentation, on utiliserait WebSockets ou SSE
        import time
        for i in range(10):
            status = {
                "backend": check_backend_running(),
                "frontend": check_frontend_running(),
                "timestamp": time.time()
            }
            yield f"data: {json.dumps(status)}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(generate(), media_type="text/event-stream")
