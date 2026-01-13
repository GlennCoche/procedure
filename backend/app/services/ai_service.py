from openai import OpenAI
from app.core.config import settings
from typing import Optional, Dict, Any, AsyncGenerator
import json

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Modèle le moins cher
        self.cache = {}  # Cache simple pour réduire les coûts
    
    async def get_chat_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> str:
        """Obtenir une réponse du chat IA avec cache"""
        # Vérifier le cache (simple hash du message)
        import hashlib
        cache_key = hashlib.md5(f"{message}{str(context)}".encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        system_prompt = self._build_system_prompt(context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            result = response.choices[0].message.content or ""
            # Mettre en cache (limiter à 100 entrées)
            if len(self.cache) > 100:
                self.cache.pop(next(iter(self.cache)))
            self.cache[cache_key] = result
            return result
        except Exception as e:
            return f"Erreur lors de la communication avec l'IA: {str(e)}"
    
    async def get_chat_response_stream(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Obtenir une réponse streamée du chat IA"""
        system_prompt = self._build_system_prompt(context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Erreur: {str(e)}"
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Construire le prompt système avec le contexte"""
        base_prompt = """Tu es un assistant technique spécialisé dans la maintenance de centrales photovoltaïques.
Tu aides les techniciens sur site à résoudre des problèmes techniques, comprendre les procédures, et fournir des conseils pratiques.
Réponds de manière claire, concise et professionnelle en français."""
        
        if context:
            if context.get("procedure_id"):
                base_prompt += f"\n\nLe technicien travaille actuellement sur la procédure ID {context['procedure_id']}."
            if context.get("step_id"):
                base_prompt += f"\nIl est à l'étape ID {context['step_id']}."
        
        return base_prompt
