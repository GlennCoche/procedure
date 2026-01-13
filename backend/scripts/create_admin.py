#!/usr/bin/env python3
"""
Script pour créer un utilisateur admin
Usage: python scripts/create_admin.py
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        email = input("Email de l'admin: ")
        password = input("Mot de passe: ")
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"L'utilisateur {email} existe déjà!")
            return
        
        # Créer l'admin
        admin = User(
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        print(f"Admin {email} créé avec succès!")
    except Exception as e:
        print(f"Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
