#!/usr/bin/env python3
"""
Générateur de steps optimisé pour les procédures
Utilise content-core MCP pour améliorer la génération de steps
"""

import json
from typing import Dict, List, Any


class StepGenerator:
    """
    Générateur de steps pour les procédures
    """
    
    def __init__(self):
        """Initialiser le générateur"""
        pass
    
    def generate_steps_from_text(self, text: str, procedure_title: str) -> List[Dict[str, Any]]:
        """
        Générer des steps depuis un texte
        
        Args:
            text: Texte contenant les instructions
            procedure_title: Titre de la procédure
        
        Returns:
            Liste de steps structurés
        """
        # Détecter les étapes numérotées
        steps = []
        
        # Patterns pour détecter les étapes
        import re
        
        # Pattern 1: "1. Titre : Instructions"
        pattern1 = r'(\d+)\.\s+([^:]+):\s*(.+?)(?=\d+\.|$)'
        matches1 = re.finditer(pattern1, text, re.MULTILINE | re.DOTALL)
        
        for match in matches1:
            step_num = int(match.group(1))
            title = match.group(2).strip()
            instructions = match.group(3).strip()
            
            steps.append({
                "step_number": step_num,
                "title": title,
                "instructions": instructions,
                "order": step_num
            })
        
        # Si aucun pattern trouvé, essayer de diviser par lignes
        if not steps:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for i, line in enumerate(lines[:20], 1):  # Limiter à 20 steps
                if len(line) > 10:  # Ignorer les lignes trop courtes
                    steps.append({
                        "step_number": i,
                        "title": line[:50] + "..." if len(line) > 50 else line,
                        "instructions": line,
                        "order": i
                    })
        
        return steps
    
    def improve_steps_with_content_core(self, steps: List[Dict[str, Any]], 
                                       procedure_context: str) -> Dict[str, Any]:
        """
        Instructions pour améliorer les steps avec content-core MCP
        
        L'agent Cursor doit utiliser: content-core.extract_content
        
        Args:
            steps: Steps à améliorer
            procedure_context: Contexte de la procédure
        
        Returns:
            Instructions pour utiliser content-core MCP
        """
        steps_text = json.dumps(steps, indent=2, ensure_ascii=False)
        
        return {
            "mcp_tool": "content-core.extract_content",
            "description": "Améliorer et optimiser les steps avec IA",
            "input": {
                "steps": steps_text,
                "context": procedure_context
            },
            "prompt": f"""
Améliore ces steps de procédure photovoltaïque pour qu'ils soient clairs et actionnables :

Contexte de la procédure : {procedure_context}

Steps actuels :
{steps_text}

Améliore :
1. La clarté des titres
2. La précision des instructions
3. L'ordre logique
4. Les informations de sécurité manquantes

Retourne les steps améliorés en JSON.
"""
        }


def generate_steps(text: str, procedure_title: str) -> List[Dict[str, Any]]:
    """Fonction utilitaire pour générer des steps"""
    generator = StepGenerator()
    return generator.generate_steps_from_text(text, procedure_title)


def main():
    """Fonction principale pour tests"""
    example_text = """
1. Préparer le site : Vérifier que le site est prêt pour l'installation
2. Installer l'onduleur : Fixer l'onduleur au mur selon les spécifications
3. Connecter les câbles : Connecter les câbles DC et AC selon le schéma
4. Vérifier les connexions : Tester toutes les connexions avant mise en service
"""
    
    generator = StepGenerator()
    steps = generator.generate_steps_from_text(example_text, "Installation onduleur")
    
    print("📝 Steps générés:")
    print(json.dumps(steps, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
