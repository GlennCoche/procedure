#!/usr/bin/env python3
"""
Script de génération d'embeddings avec connexion directe à Supabase
Évite les problèmes d'authentification API
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm
import time

# Ajouter les chemins
scripts_dir = Path(__file__).parent
project_root = scripts_dir.parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI non installé. Installation: pip install openai")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("⚠️  psycopg2 non installé. Installation: pip install psycopg2-binary")


class EmbeddingGeneratorDirect:
    """Génération d'embeddings avec connexion directe à Supabase"""
    
    def __init__(self, database_url: str = None, openai_api_key: str = None):
        self.db_conn = None
        self.openai_client = None
        
        # Configuration base de données
        if database_url:
            self.database_url = database_url
        else:
            # Essayer depuis les variables d'environnement
            self.database_url = os.getenv("DATABASE_URL")
            if not self.database_url:
                # Essayer depuis frontend/.env.local
                env_file = project_root / "frontend" / ".env.local"
                if env_file.exists():
                    with open(env_file) as f:
                        for line in f:
                            if line.startswith("DATABASE_URL="):
                                self.database_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                                break
        
        # Configuration OpenAI
        if openai_api_key:
            self.openai_api_key = openai_api_key
        else:
            # Essayer depuis les variables d'environnement
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                # Essayer depuis backend/.env
                env_file = project_root / "backend" / ".env"
                if env_file.exists():
                    with open(env_file) as f:
                        for line in f:
                            if line.startswith("OPENAI_API_KEY="):
                                self.openai_api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                                break
        
        if not self.database_url:
            raise ValueError("DATABASE_URL non trouvé. Spécifiez --database-url ou configurez DATABASE_URL")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY non trouvé. Spécifiez --openai-key ou configurez OPENAI_API_KEY")
        
        # Initialiser les clients
        if OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        if PSYCOPG2_AVAILABLE:
            self.db_conn = psycopg2.connect(self.database_url)
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Générer un embedding pour un texte"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]  # Limiter la longueur
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Erreur génération embedding: {e}")
            return None
    
    def get_procedures(self, limit: int = None) -> List[Dict[str, Any]]:
        """Récupérer toutes les procédures depuis la base de données"""
        if not self.db_conn:
            return []
        
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            query = "SELECT id, title, description, category, tags FROM procedures WHERE is_active = true"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Erreur récupération procédures: {e}")
            return []
    
    def get_tips(self, limit: int = None) -> List[Dict[str, Any]]:
        """Récupérer tous les tips depuis la base de données"""
        if not self.db_conn:
            return []
        
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            query = "SELECT id, title, content, category, tags FROM tips"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Erreur récupération tips: {e}")
            return []
    
    def save_embedding(self, document_type: str, document_id: int, content: str, embedding: List[float], metadata: Dict[str, Any] = None) -> bool:
        """Sauvegarder un embedding dans la base de données"""
        if not self.db_conn:
            return False
        
        try:
            cursor = self.db_conn.cursor()
            
            # Convertir l'embedding en format PostgreSQL vector
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            metadata_str = json.dumps(metadata or {})
            
            # Vérifier si l'embedding existe déjà
            cursor.execute(
                "SELECT id FROM document_embeddings WHERE document_type = %s AND document_id = %s",
                (document_type, document_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Mettre à jour
                cursor.execute(
                    """
                    UPDATE document_embeddings 
                    SET content = %s, embedding = %s::vector, metadata = %s
                    WHERE document_type = %s AND document_id = %s
                    """,
                    (content, embedding_str, metadata_str, document_type, document_id)
                )
            else:
                # Insérer
                cursor.execute(
                    """
                    INSERT INTO document_embeddings (document_type, document_id, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s::vector, %s)
                    """,
                    (document_type, document_id, content, embedding_str, metadata_str)
                )
            
            self.db_conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde embedding: {e}")
            self.db_conn.rollback()
            return False
    
    def generate_all(self, limit: int = None) -> Dict[str, Any]:
        """Générer les embeddings pour toutes les procédures et tips"""
        if not self.openai_client:
            print("❌ Client OpenAI non configuré")
            return {"error": "OpenAI non configuré"}
        
        if not self.db_conn:
            print("❌ Connexion base de données non configurée")
            return {"error": "Base de données non configurée"}
        
        print("🚀 Génération des embeddings...")
        
        # Procédures
        print("📋 Récupération des procédures...")
        procedures = self.get_procedures(limit)
        print(f"📊 {len(procedures)} procédures trouvées")
        
        proc_results = {"processed": 0, "errors": []}
        for proc in tqdm(procedures, desc="Génération embeddings procédures"):
            proc_id = proc["id"]
            title = proc.get("title", "")
            description = proc.get("description", "") or ""
            
            content = f"{title}\n\n{description}".strip()
            if not content:
                continue
            
            embedding = self.generate_embedding(content)
            if embedding:
                metadata = {
                    "title": title,
                    "category": proc.get("category"),
                    "tags": proc.get("tags")
                }
                
                if self.save_embedding("procedure", proc_id, content, embedding, metadata):
                    proc_results["processed"] += 1
                else:
                    proc_results["errors"].append(f"Procédure {proc_id}")
            else:
                proc_results["errors"].append(f"Procédure {proc_id}: erreur génération")
            
            time.sleep(0.1)  # Respecter les limites de taux
        
        # Tips
        print("\n📋 Récupération des tips...")
        tips = self.get_tips(limit)
        print(f"📊 {len(tips)} tips trouvés")
        
        tip_results = {"processed": 0, "errors": []}
        for tip in tqdm(tips, desc="Génération embeddings tips"):
            tip_id = tip["id"]
            title = tip.get("title", "")
            content_text = tip.get("content", "") or ""
            
            content = f"{title}\n\n{content_text}".strip()
            if not content:
                continue
            
            embedding = self.generate_embedding(content)
            if embedding:
                metadata = {
                    "title": title,
                    "category": tip.get("category"),
                    "tags": tip.get("tags")
                }
                
                if self.save_embedding("tip", tip_id, content, embedding, metadata):
                    tip_results["processed"] += 1
                else:
                    tip_results["errors"].append(f"Tip {tip_id}")
            else:
                tip_results["errors"].append(f"Tip {tip_id}: erreur génération")
            
            time.sleep(0.1)
        
        total = {
            "procedures": proc_results,
            "tips": tip_results,
            "total_processed": proc_results["processed"] + tip_results["processed"],
            "total_errors": len(proc_results["errors"]) + len(tip_results["errors"])
        }
        
        print(f"\n✅ Génération terminée:")
        print(f"  - Procédures: {proc_results['processed']}")
        print(f"  - Tips: {tip_results['processed']}")
        print(f"  - Total: {total['total_processed']}")
        if total["total_errors"] > 0:
            print(f"  - Erreurs: {total['total_errors']}")
        
        return total
    
    def close(self):
        """Fermer la connexion"""
        if self.db_conn:
            self.db_conn.close()


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Générer les embeddings avec connexion directe à Supabase")
    parser.add_argument("--database-url", type=str, help="URL de connexion PostgreSQL (ou utiliser DATABASE_URL)")
    parser.add_argument("--openai-key", type=str, help="Clé API OpenAI (ou utiliser OPENAI_API_KEY)")
    parser.add_argument("--limit", type=int, help="Limiter le nombre de documents")
    
    args = parser.parse_args()
    
    try:
        generator = EmbeddingGeneratorDirect(
            database_url=args.database_url,
            openai_api_key=args.openai_key
        )
        
        generator.generate_all(args.limit)
        generator.close()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
