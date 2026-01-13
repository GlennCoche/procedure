#!/usr/bin/env python3
"""
Script simplifié pour démarrer les serveurs
Peut être appelé depuis l'API
"""

import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Démarrer le backend"""
    backend_dir = Path(__file__).parent.parent
    venv_python = backend_dir / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("❌ Environnement virtuel non trouvé")
        return None
    
    process = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

def start_frontend():
    """Démarrer le frontend"""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    
    if not (frontend_dir / "node_modules").exists():
        print("❌ Dépendances npm non installées")
        return None
    
    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

if __name__ == "__main__":
    print("🚀 Démarrage des serveurs...")
    backend = start_backend()
    frontend = start_frontend()
    
    if backend and frontend:
        print("✅ Serveurs démarrés")
        try:
            backend.wait()
            frontend.wait()
        except KeyboardInterrupt:
            backend.terminate()
            frontend.terminate()
