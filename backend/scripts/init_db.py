#!/usr/bin/env python3
"""
Script pour initialiser la base de données
Usage: python scripts/init_db.py
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import *  # Import all models

def init_db():
    """Créer toutes les tables"""
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès!")

if __name__ == "__main__":
    init_db()
