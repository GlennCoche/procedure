#!/usr/bin/env python3
"""
Prompts experts avancés pour l'analyse et l'enrichissement 
de documentation photovoltaïque
"""

import json
from typing import Dict, List, Any

# =============================================================================
# PROMPT D'ANALYSE EXPERT
# =============================================================================

EXPERT_ANALYSIS_PROMPT = """
Tu es un expert senior en maintenance photovoltaïque avec 25 ans d'expérience sur le terrain.

Document à analyser : {document_title}
Marque : {brand}
Type : {file_type}

TÂCHES D'ANALYSE APPROFONDIE:

1. IDENTIFICATION DU DOCUMENT
   - Type exact (manuel installation, guide maintenance, référence alarmes, fiche technique)
   - Équipement concerné (onduleur, optimiseur, batterie, monitoring)
   - Public cible (installateur, technicien, utilisateur final)
   - Version et date si disponibles

2. EXTRACTION DE STRUCTURE
   - Sections principales avec hiérarchie complète
   - Procédures techniques détaillées avec TOUTES les étapes
   - Points d'attention critiques
   - Références croisées entre sections

3. PROCÉDURES TECHNIQUES
   Pour CHAQUE procédure identifiée:
   - Titre clair et descriptif
   - Prérequis (outils, conditions, EPI)
   - Étapes numérotées avec détails complets
   - Points de vérification intermédiaires
   - Valeurs de référence (tensions, temps, températures)
   - Avertissements de sécurité

4. CONSEILS ET TIPS
   - Astuces de techniciens expérimentés
   - Erreurs courantes à éviter
   - Gains de temps
   - Alternatives en cas de problème

5. INFORMATIONS CRITIQUES
   - Tous les paramètres de sécurité
   - Valeurs limites techniques
   - Codes d'erreur avec solutions
   - Contacts support technique

6. PARAMÈTRES FRANCE
   - Configurations spécifiques France métropolitaine
   - Normes et standards applicables (NF C 15-100, UTE C 15-712)
   - Seuils de tension/fréquence réseau France

FORMAT DE RÉPONSE JSON:
{{
  "document_info": {{
    "type": "manual|guide|datasheet|reference",
    "equipment_type": "onduleur|optimiseur|batterie|monitoring",
    "brand": "...",
    "model": "...",
    "version": "...",
    "target_audience": "installer|technician|user"
  }},
  "structure": [
    {{
      "title": "...",
      "level": 1,
      "page_start": null,
      "subsections": [...]
    }}
  ],
  "procedures": [
    {{
      "title": "...",
      "description": "...",
      "category": "installation|configuration|maintenance|depannage",
      "prerequisites": {{
        "tools": [...],
        "conditions": [...],
        "safety_equipment": [...]
      }},
      "estimated_time": "...",
      "difficulty": "easy|medium|hard|expert",
      "steps": [
        {{
          "order": 1,
          "title": "...",
          "instructions": "...",
          "verification": "...",
          "reference_values": {{}},
          "warnings": [...],
          "sub_steps": [...]
        }}
      ],
      "troubleshooting": [...],
      "tags": [...]
    }}
  ],
  "tips": [
    {{
      "title": "...",
      "content": "...",
      "category": "...",
      "importance": "high|medium|low",
      "source_section": "...",
      "tags": [...]
    }}
  ],
  "critical_info": {{
    "safety_warnings": [...],
    "error_codes": [
      {{"code": "...", "meaning": "...", "solution": "..."}}
    ],
    "reference_values": {{}},
    "france_specific": {{
      "network_standard": "...",
      "voltage_thresholds": {{}},
      "frequency_range": {{}}
    }}
  }},
  "settings_france": [
    {{
      "category": "tension|frequence|puissance|reseau|protection",
      "name": "...",
      "value": "...",
      "unit": "...",
      "source_page": null,
      "notes": "..."
    }}
  ]
}}
"""

# =============================================================================
# PROMPT D'ENRICHISSEMENT AVANCÉ
# =============================================================================

ADVANCED_ENRICHMENT_PROMPT = """
Tu es un FORMATEUR EXPERT en maintenance photovoltaïque avec 25 ans d'expérience terrain.
Tu formes des techniciens débutants et confirmés.

PROCÉDURE À ENRICHIR:
{procedure_data}

CONTEXTE DU DOCUMENT SOURCE:
{document_context}

EXIGENCES D'ENRICHISSEMENT ULTRA-DÉTAILLÉ:

1. DESCRIPTION COMPLÈTE
   Enrichis la description pour inclure:
   - QUAND faire cette procédure (contexte d'intervention)
   - POURQUOI c'est important (conséquences si mal fait)
   - PRÉREQUIS COMPLETS:
     * Outils avec références exactes si possible
     * EPI obligatoires et recommandés
     * Conditions météo/environnement
     * État de l'installation avant intervention
   - TEMPS ESTIMÉ réaliste
   - NIVEAU DE DIFFICULTÉ justifié

2. ÉTAPES ULTRA-DÉTAILLÉES
   Pour CHAQUE étape existante, ajoute:
   - Instructions PAS-À-PAS (divise en sub-steps si > 3 actions)
   - Points de vérification AVANT de passer à la suite
   - VALEURS NUMÉRIQUES précises:
     * Tensions attendues (Vdc, Vac)
     * Courants (Idc, Iac)
     * Couples de serrage (Nm)
     * Températures limites
   - PHOTOS/SCHÉMAS attendus (décris ce qu'on devrait voir)
   - ERREURS COURANTES à éviter
   - QUE FAIRE SI le résultat n'est pas celui attendu

3. CONSEILS TERRAIN
   Ajoute pour chaque étape pertinente:
   - Astuces de techniciens expérimentés ("sur le terrain, on fait plutôt...")
   - Pièges classiques et comment les éviter
   - Gains de temps possibles
   - Bonnes pratiques sécurité

4. TROUBLESHOOTING
   Ajoute une section dépannage avec:
   - Problèmes fréquents par étape
   - Solutions rapides
   - Quand escalader vers le support
   - Informations à collecter avant d'appeler

5. MISE EN GARDE SÉCURITÉ
   - Risques électriques spécifiques
   - Risques mécaniques
   - Travail en hauteur si applicable
   - Conduite à tenir en cas d'incident

FORMAT: Même structure JSON que l'entrée, mais BEAUCOUP plus détaillé.
Conserve TOUS les champs existants et enrichis-les.
"""

# =============================================================================
# PROMPT DE STRUCTURATION
# =============================================================================

STRUCTURING_PROMPT = """
Transforme cette analyse de document en structures applicatives prêtes pour l'import.

ANALYSE DU DOCUMENT:
{analysis_data}

TÂCHES DE STRUCTURATION:

1. PROCÉDURES
   - Crée une procédure par section technique identifiée
   - Génère des steps depuis les instructions numérotées
   - Assure la cohérence titre/description/steps
   - Catégorise correctement (installation, configuration, maintenance, dépannage)

2. TIPS
   - Extrais les conseils et astuces importants
   - Un tip par conseil distinct
   - Catégorise par thème
   - Indique la source dans le document

3. RÉGLAGES FRANCE
   - Extrais TOUS les paramètres France
   - Organise par catégorie
   - Inclus les valeurs et unités

4. TAGS INTELLIGENTS
   - Génère des tags pertinents pour la recherche
   - Inclus: marque, modèle, type d'action, composants

FORMAT JSON:
{{
  "procedures": [
    {{
      "title": "...",
      "description": "...",
      "category": "installation|configuration|maintenance|depannage",
      "tags": [...],
      "estimated_time": "...",
      "difficulty": "easy|medium|hard|expert",
      "steps": [
        {{
          "order": 1,
          "title": "...",
          "description": "...",
          "instructions": "...",
          "verification": "...",
          "warnings": [...]
        }}
      ]
    }}
  ],
  "tips": [
    {{
      "title": "...",
      "content": "...",
      "category": "...",
      "tags": [...],
      "importance": "high|medium|low"
    }}
  ],
  "settings": [
    {{
      "brand": "...",
      "equipment_type": "...",
      "model": "...",
      "category": "...",
      "name": "...",
      "value": "...",
      "unit": "...",
      "country": "FR",
      "notes": "..."
    }}
  ]
}}
"""

# =============================================================================
# PROMPT DE VALIDATION QUALITÉ
# =============================================================================

VALIDATION_PROMPT = """
Valide la qualité de cette procédure/tip pour garantir son utilité terrain.

DONNÉES À VALIDER:
{data_to_validate}

CRITÈRES DE VALIDATION:

1. COMPLÉTUDE (30 points)
   - Titre clair et descriptif
   - Description du contexte
   - Prérequis mentionnés
   - Toutes les étapes présentes
   - Pas d'information manquante critique

2. CLARTÉ (25 points)
   - Instructions compréhensibles par un technicien junior
   - Pas d'ambiguïté
   - Vocabulaire technique correct
   - Structure logique

3. PRÉCISION TECHNIQUE (25 points)
   - Valeurs numériques présentes quand nécessaire
   - Références correctes (composants, outils)
   - Cohérence technique
   - Avertissements de sécurité pertinents

4. UTILITÉ TERRAIN (20 points)
   - Actionnable directement
   - Conseils pratiques
   - Points de vérification
   - Gestion des cas problématiques

RÉPONSE JSON:
{{
  "quality_score": 0.85,
  "scores": {{
    "completude": 25,
    "clarte": 22,
    "precision": 20,
    "utilite": 18
  }},
  "needs_review": false,
  "issues": [
    {{
      "severity": "low|medium|high",
      "field": "...",
      "issue": "...",
      "suggestion": "..."
    }}
  ],
  "validation_notes": "..."
}}
"""

# =============================================================================
# PROMPT EXTRACTION RÉGLAGES FRANCE
# =============================================================================

SETTINGS_EXTRACTION_PROMPT = """
Tu es un expert en normes et réglementation photovoltaïque française.

DOCUMENT À ANALYSER:
{document_content}

MARQUE: {brand}
TYPE D'ÉQUIPEMENT: {equipment_type}

EXTRAIS TOUS LES PARAMÈTRES SPÉCIFIQUES À LA FRANCE MÉTROPOLITAINE:

CATÉGORIES À RECHERCHER:

1. TENSION RÉSEAU
   - Tension nominale (230V/400V)
   - Seuils de déclenchement (Vmin, Vmax)
   - Plages de fonctionnement
   - Temps de reconnexion

2. FRÉQUENCE RÉSEAU
   - Fréquence nominale (50Hz)
   - Plage de fonctionnement (47.5-51.5Hz typique)
   - Seuils de déclenchement

3. PUISSANCE
   - Limites de puissance injectée
   - Courbes de derating
   - Limitation de puissance active
   - Facteur de puissance

4. STANDARDS RÉSEAU
   - Code pays France (souvent 0D, FR, etc.)
   - Norme applicable (VDE 0126, CEI, NF C 15-100)
   - Configuration des interrupteurs/DIP switches

5. COMMUNICATION
   - Paramètres RS485 par défaut
   - Adresses Modbus
   - Protocoles supportés

6. PROTECTION
   - Protection différentielle requise
   - Type de disjoncteur
   - Seuils de protection internes

7. INJECTION RÉSEAU
   - Paramètres anti-îlotage
   - Zero injection si applicable
   - Limitation d'export

FORMAT JSON:
[
  {{
    "category": "TENSION|FREQUENCE|PUISSANCE|RESEAU|COMMUNICATION|PROTECTION|INJECTION",
    "name": "Nom du paramètre",
    "value": "Valeur",
    "unit": "Unité (V, Hz, W, %)",
    "country": "FR",
    "equipment_type": "onduleur|optimiseur|batterie",
    "source_section": "Section du document",
    "page_number": null,
    "notes": "Notes additionnelles",
    "importance": "critical|standard|optional"
  }}
]

IMPORTANT: 
- Extrais TOUTES les valeurs trouvées, même partielles
- Indique clairement la source (page, section)
- Distingue les valeurs obligatoires des optionnelles
"""


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_expert_analysis_prompt(document_title: str, brand: str, file_type: str) -> str:
    """Obtenir le prompt d'analyse expert formaté"""
    return EXPERT_ANALYSIS_PROMPT.format(
        document_title=document_title,
        brand=brand,
        file_type=file_type
    )


def get_enrichment_prompt(procedure_data: Dict, document_context: str = "") -> str:
    """Obtenir le prompt d'enrichissement formaté"""
    return ADVANCED_ENRICHMENT_PROMPT.format(
        procedure_data=json.dumps(procedure_data, indent=2, ensure_ascii=False),
        document_context=document_context
    )


def get_structuring_prompt(analysis_data: Dict) -> str:
    """Obtenir le prompt de structuration formaté"""
    return STRUCTURING_PROMPT.format(
        analysis_data=json.dumps(analysis_data, indent=2, ensure_ascii=False)
    )


def get_validation_prompt(data_to_validate: Dict) -> str:
    """Obtenir le prompt de validation formaté"""
    return VALIDATION_PROMPT.format(
        data_to_validate=json.dumps(data_to_validate, indent=2, ensure_ascii=False)
    )


def get_settings_extraction_prompt(document_content: str, brand: str, equipment_type: str) -> str:
    """Obtenir le prompt d'extraction des réglages France"""
    return SETTINGS_EXTRACTION_PROMPT.format(
        document_content=document_content[:50000],  # Limiter la taille
        brand=brand,
        equipment_type=equipment_type
    )


# =============================================================================
# PROMPTS SUPPLÉMENTAIRES POUR CAS SPÉCIFIQUES
# =============================================================================

ERROR_CODE_ANALYSIS_PROMPT = """
Analyse ce tableau de codes d'erreur et génère une structure exploitable:

CONTENU:
{error_codes_content}

Pour CHAQUE code d'erreur, extrais:
- Code exact
- Signification
- Causes possibles
- Solutions recommandées
- Gravité (critical/warning/info)

FORMAT JSON:
[
  {{
    "code": "E001",
    "name": "Nom de l'erreur",
    "meaning": "Description",
    "causes": ["cause1", "cause2"],
    "solutions": ["solution1", "solution2"],
    "severity": "critical|warning|info",
    "requires_intervention": true
  }}
]
"""

WIRING_DIAGRAM_ANALYSIS_PROMPT = """
Analyse ce schéma de câblage et décris:

1. Composants identifiés
2. Connexions entre composants
3. Points de mesure importants
4. Sections de câble recommandées
5. Points d'attention pour l'installation

Génère une description textuelle détaillée utilisable dans une procédure.
"""


if __name__ == "__main__":
    print("📝 Prompts experts pour documentation photovoltaïque")
    print("=" * 50)
    print("\nPrompts disponibles:")
    print("  - EXPERT_ANALYSIS_PROMPT: Analyse complète de document")
    print("  - ADVANCED_ENRICHMENT_PROMPT: Enrichissement détaillé")
    print("  - STRUCTURING_PROMPT: Conversion en structures applicatives")
    print("  - VALIDATION_PROMPT: Validation qualité")
    print("  - SETTINGS_EXTRACTION_PROMPT: Extraction réglages France")
