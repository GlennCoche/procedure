"""
Service de recherche vectorielle pour les procédures et tips
Utilise pgvector pour la recherche sémantique
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.core.config import settings


class VectorSearchService:
    """Service pour la recherche vectorielle"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = None
        
        # Initialiser le client OpenAI si disponible
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
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
            print(f"Erreur génération embedding: {e}")
            return None
    
    def search_similar(
        self,
        query: str,
        document_type: Optional[str] = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Rechercher des documents similaires à une requête
        
        Args:
            query: Texte de la requête
            document_type: Type de document ('procedure' ou 'tip'), None pour tous
            limit: Nombre de résultats
            threshold: Seuil de similarité (0-1)
        
        Returns:
            Liste de documents avec score de similarité
        """
        # Générer l'embedding de la requête
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        # Construire la requête SQL
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Requête SQL pour recherche vectorielle
        sql = """
        SELECT 
            id,
            document_type,
            document_id,
            content,
            metadata,
            1 - (embedding <=> :embedding::vector) as similarity
        FROM document_embeddings
        WHERE embedding IS NOT NULL
        """
        
        params = {"embedding": embedding_str}
        
        # Filtrer par type si spécifié
        if document_type:
            sql += " AND document_type = :document_type"
            params["document_type"] = document_type
        
        # Filtrer par seuil de similarité
        sql += " AND (1 - (embedding <=> :embedding::vector)) >= :threshold"
        params["threshold"] = threshold
        
        # Trier par similarité et limiter
        sql += " ORDER BY similarity DESC LIMIT :limit"
        params["limit"] = limit
        
        try:
            result = self.db.execute(text(sql), params)
            rows = result.fetchall()
            
            # Formater les résultats
            results = []
            for row in rows:
                metadata = {}
                if row.metadata:
                    try:
                        metadata = json.loads(row.metadata) if isinstance(row.metadata, str) else row.metadata
                    except:
                        pass
                
                results.append({
                    "id": row.id,
                    "document_type": row.document_type,
                    "document_id": row.document_id,
                    "content": row.content,
                    "metadata": metadata,
                    "similarity": float(row.similarity)
                })
            
            return results
        except Exception as e:
            print(f"Erreur recherche vectorielle: {e}")
            return []
    
    def search_procedures(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Rechercher des procédures similaires"""
        return self.search_similar(query, document_type="procedure", limit=limit)
    
    def search_tips(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Rechercher des tips similaires"""
        return self.search_similar(query, document_type="tip", limit=limit)
    
    def search_all(self, query: str, limit: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Rechercher dans toutes les procédures et tips"""
        procedures = self.search_procedures(query, limit=limit)
        tips = self.search_tips(query, limit=limit)
        
        return {
            "procedures": procedures,
            "tips": tips
        }


def get_vector_search_service(db: Session) -> VectorSearchService:
    """Factory pour créer une instance du service"""
    return VectorSearchService(db)
