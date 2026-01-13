---
name: Plan Intelligent Import Documentation Photovoltaïque
overview: Plan hybride combinant extraction automatique et analyse IA experte pour transformer les 741 documents techniques en base de connaissances structurée, validée et enrichie, prête pour l'import dans l'application.
todos:
  - id: create_local_db
    content: Créer la base SQLite locale avec schéma de validation (document_processing, document_images, local_procedures, local_tips)
    status: pending
  - id: enhance_extraction
    content: Améliorer extraction PDF pour inclure images, OCR, et métadonnées complètes
    status: pending
  - id: create_ai_analyzer
    content: Créer l'analyseur IA contextuel avec prompts expert photovoltaïque
    status: pending
    dependencies:
      - enhance_extraction
  - id: create_vision_analyzer
    content: Créer l'analyseur d'images avec Vision API pour comprendre schémas et graphiques
    status: pending
    dependencies:
      - enhance_extraction
  - id: create_intelligent_structurer
    content: Créer le structurateur intelligent qui transforme l'analyse IA en procédures/steps/tips
    status: pending
    dependencies:
      - create_ai_analyzer
  - id: create_ai_enricher
    content: Créer l'enrichisseur IA qui améliore et complète les données générées
    status: pending
    dependencies:
      - create_intelligent_structurer
  - id: create_validator
    content: Créer le validateur de qualité avec scores et détection de problèmes
    status: pending
    dependencies:
      - create_ai_enricher
  - id: create_orchestrator
    content: Créer le script principal d'orchestration qui gère le workflow complet document par document
    status: pending
    dependencies:
      - create_validator
  - id: test_pipeline
    content: Tester le pipeline complet sur un document ABB pour valider le workflow
    status: pending
    dependencies:
      - create_orchestrator
  - id: process_all_documents
    content: Traiter tous les documents par marque avec le pipeline intelligent
    status: pending
    dependencies:
      - test_pipeline
  - id: create_migration_script
    content: Créer le script de migration depuis SQLite local vers Supabase production
    status: pending
    dependencies:
      - process_all_documents
  - id: import_validated_data
    content: Importer les données validées dans Supabase et générer les embeddings
    status: pending
    dependencies:
      - create_migration_script
---

# Plan Intelligent d'Import de Documentation Photovoltaïque

## Analyse de l'Approche Proposée

### ✅ Points Forts de Votre Suggestion

1. **Traitement document par document** : Permet un contrôle qualité fin
2. **Compréhension contextuelle** : L'IA comprend le contenu, pas juste extraction
3. **Base locale de validation** : Permet révision avant import production
4. **Enrichissement intelligent** : L'IA améliore et complète les données
5. **Expertise métier** : L'agent se comporte comme un expert photovoltaïque

### 🔄 Améliorations Proposées

1. **Pipeline hybride** : Automatisation pour extraction + IA pour compréhension
2. **Base SQLite locale** : Même schéma que production pour validation
3. **Workflow itératif** : Extraction → Analyse IA → Validation → Enrichissement → Import
4. **Gestion des images** : Vision API pour comprendre schémas et graphiques
5. **Qualité progressive** : Plusieurs passes d'enrichissement

## Architecture du Système

### Pipeline de Traitement

```
Document Source (PDF/MMS)
  ↓
[Phase 1: Extraction Automatique]
  → Texte brut
  → Images extraites
  → Métadonnées
  ↓
[Phase 2: Base Locale SQLite]
  → Stockage brut structuré
  → État: "extracted"
  ↓
[Phase 3: Analyse IA Contextuelle]
  → Compréhension du document
  → Identification du type (manuel, procédure, alarme, etc.)
  → Détection de la structure logique
  → Analyse des images/schémas
  → État: "analyzed"
  ↓
[Phase 4: Génération Structurée]
  → Création procédures/steps
  → Extraction tips
  → Génération métadonnées enrichies
  → État: "structured"
  ↓
[Phase 5: Enrichissement IA Expert]
  → Validation technique
  → Complétion d'informations manquantes
  → Optimisation des descriptions
  → Génération de conseils additionnels
  → État: "enriched"
  ↓
[Phase 6: Validation Finale]
  → Vérification cohérence
  → Détection doublons
  → Qualité des données
  → État: "validated"
  ↓
[Phase 7: Import Production]
  → Migration vers Supabase
  → Génération embeddings
  → Indexation
```

## Structure de la Base Locale SQLite

### Schéma de Validation

```sql
-- Table pour suivre le traitement des documents
CREATE TABLE document_processing (
    id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    brand TEXT,
    file_type TEXT,
    file_size INTEGER,
    status TEXT, -- 'pending', 'extracted', 'analyzed', 'structured', 'enriched', 'validated', 'imported', 'error'
    extraction_data TEXT, -- JSON avec texte brut, images, etc.
    analysis_data TEXT, -- JSON avec analyse IA
    structured_data TEXT, -- JSON avec procédures/steps générés
    enriched_data TEXT, -- JSON avec données enrichies
    validation_notes TEXT, -- Notes de validation
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les images extraites
CREATE TABLE document_images (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES document_processing(id),
    image_path TEXT,
    image_type TEXT, -- 'diagram', 'photo', 'graph', 'table'
    description TEXT, -- Description générée par Vision API
    extracted_text TEXT, -- Texte OCR si applicable
    page_number INTEGER,
    position_in_doc TEXT
);

-- Table pour les procédures générées (local)
CREATE TABLE local_procedures (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES document_processing(id),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    tags TEXT, -- JSON
    steps TEXT, -- JSON array
    quality_score REAL, -- Score de qualité 0-1
    needs_review BOOLEAN DEFAULT 0,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les tips générés (local)
CREATE TABLE local_tips (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES document_processing(id),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    tags TEXT, -- JSON
    source_section TEXT, -- Section du document source
    quality_score REAL,
    needs_review BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Phases d'Implémentation

### Phase 1 : Infrastructure de Base Locale

**Objectif** : Créer la base SQLite locale avec schéma de validation

**Fichiers à créer** :

- `scripts/local_db/schema.sql` - Schéma SQLite
- `scripts/local_db/db_manager.py` - Gestionnaire de base locale
- `scripts/local_db/migrations/` - Migrations locales

### Phase 2 : Extraction Améliorée avec Images

**Objectif** : Extraire texte + images + métadonnées

**Améliorations** :

- Extraction images depuis PDFs
- OCR pour images scannées
- Détection type d'image (schéma, photo, graphique)
- Stockage images dans `scripts/local_db/images/`

**Fichiers à créer/modifier** :

- `scripts/extract_pdf_enhanced.py` - Extraction avec images
- `scripts/extract_images.py` - Gestion images

### Phase 3 : Analyse IA Contextuelle

**Objectif** : Comprendre le document comme un expert

**Fonctionnalités** :

- Classification du type de document
- Identification de la structure logique
- Détection des sections importantes
- Analyse des images avec Vision API
- Génération de métadonnées contextuelles

**Prompt système expert** :

```
Tu es un expert en maintenance et installation d'équipements photovoltaïques avec 20 ans d'expérience.
Tu analyses des documents techniques (manuels, procédures, guides) pour en extraire les connaissances pratiques.

Pour chaque document, identifie :
1. Le type de document (manuel installation, guide maintenance, référence alarmes, etc.)
2. La marque et le modèle d'équipement
3. La structure logique (sections, chapitres, procédures)
4. Les procédures techniques détaillées
5. Les conseils pratiques et astuces
6. Les informations critiques (sécurité, paramètres, contacts)
7. Les schémas et diagrammes importants

Génère des données structurées de haute qualité, prêtes pour être utilisées par des techniciens sur site.
```

**Fichiers à créer** :

- `scripts/ai_analyzer.py` - Analyseur IA contextuel
- `scripts/prompts/expert_prompts.py` - Prompts spécialisés

### Phase 4 : Génération Structurée Intelligente

**Objectif** : Transformer l'analyse en structures applicatives

**Processus** :

- Création procédures depuis sections identifiées
- Extraction steps depuis instructions numérotées
- Génération tips depuis conseils détectés
- Association images aux steps pertinents
- Génération tags intelligents

**Fichiers à créer** :

- `scripts/intelligent_structurer.py` - Structuration intelligente
- `scripts/step_generator.py` - Génération steps optimisée

### Phase 5 : Enrichissement IA Expert

**Objectif** : Améliorer et compléter les données

**Enrichissements** :

- Validation technique des procédures
- Complétion d'informations manquantes
- Optimisation des descriptions pour clarté
- Génération de conseils additionnels
- Détection et correction d'erreurs
- Amélioration des tags et catégories

**Fichiers à créer** :

- `scripts/ai_enricher.py` - Enrichisseur IA
- `scripts/quality_validator.py` - Validateur qualité

### Phase 6 : Validation et Révision

**Objectif** : Vérifier qualité avant import

**Validations** :

- Cohérence des données
- Détection doublons
- Complétude des procédures
- Qualité des descriptions
- Présence d'étapes critiques

**Fichiers à créer** :

- `scripts/validator.py` - Validateur complet
- `scripts/review_interface.py` - Interface de révision (optionnel)

### Phase 7 : Import Production

**Objectif** : Migrer vers Supabase avec qualité garantie

**Processus** :

- Migration depuis SQLite local vers Supabase
- Génération embeddings optimisés
- Indexation vectorielle
- Vérification post-import

**Fichiers à créer** :

- `scripts/migrate_to_production.py` - Migration production
- `scripts/import_validator.py` - Validation post-import

## Workflow d'Exécution

### Traitement Document par Document

Pour chaque document dans `docs/` :

1. **Extraction** (automatique)
   ```python
   extract_document(file_path) → extraction_data
   save_to_local_db(file_path, extraction_data, status='extracted')
   ```

2. **Analyse IA** (intelligent)
   ```python
   analysis = ai_analyze_document(extraction_data, expert_prompt)
   update_local_db(file_path, analysis_data=analysis, status='analyzed')
   ```

3. **Structuration** (intelligent)
   ```python
   structured = intelligent_structure(analysis_data)
   save_procedures_to_local(structured['procedures'])
   save_tips_to_local(structured['tips'])
   update_local_db(file_path, structured_data=structured, status='structured')
   ```

4. **Enrichissement** (intelligent)
   ```python
   enriched = ai_enrich(structured_data, expert_prompt)
   update_local_db(file_path, enriched_data=enriched, status='enriched')
   ```

5. **Validation** (automatique + IA)
   ```python
   validation = validate_data(enriched_data)
   if validation.passed:
       update_local_db(file_path, status='validated')
   else:
       update_local_db(file_path, status='needs_review', validation_notes=...)
   ```

6. **Import** (automatique)
   ```python
   if status == 'validated':
       import_to_production(enriched_data)
       generate_embeddings(enriched_data)
       update_local_db(file_path, status='imported')
   ```


## Prompts IA Expert

### Prompt Principal d'Analyse

```python
EXPERT_ANALYSIS_PROMPT = """
Tu es un expert senior en maintenance photovoltaïque avec 20 ans d'expérience sur le terrain.

Document à analyser : {document_title}
Marque : {brand}
Type : {file_type}

Tâches :
1. Identifie le type de document (manuel installation, guide maintenance, référence alarmes, configuration, etc.)
2. Extrais la structure logique (sections principales, procédures, étapes)
3. Identifie les procédures techniques détaillées avec leurs étapes
4. Extrais les conseils pratiques, astuces, et informations critiques
5. Analyse les images/schémas fournis et génère des descriptions pertinentes
6. Identifie les informations de sécurité importantes
7. Extrais les paramètres techniques, valeurs de référence, contacts

Format de réponse JSON structuré :
{
  "document_type": "...",
  "equipment_brand": "...",
  "equipment_model": "...",
  "main_sections": [...],
  "procedures_detected": [...],
  "tips_detected": [...],
  "critical_info": {...},
  "images_analysis": [...]
}
"""
```

### Prompt d'Enrichissement

```python
ENRICHMENT_PROMPT = """
En tant qu'expert photovoltaïque, enrichis cette procédure pour qu'elle soit optimale pour des techniciens sur site :

Procédure actuelle :
{procedure_data}

Améliore :
1. Les descriptions pour plus de clarté
2. Les instructions pour plus de précision
3. Ajoute des conseils pratiques manquants
4. Identifie les points d'attention critiques
5. Optimise les tags et catégories
6. Vérifie la cohérence technique

Génère la version enrichie en JSON.
"""
```

## Gestion des Images

### Extraction et Analyse

1. **Extraction** : Extraire toutes les images des PDFs
2. **Classification** : Détecter type (schéma, photo, graphique, tableau)
3. **Vision API** : Analyser avec GPT-4o Vision pour description
4. **OCR** : Extraire texte si image contient du texte
5. **Association** : Lier images aux sections/steps pertinents

### Stockage

- Images dans `scripts/local_db/images/{document_id}/`
- Métadonnées dans table `document_images`
- Descriptions dans base locale
- Références dans procédures/steps

## Qualité et Validation

### Scores de Qualité

- **Complétude** : Toutes les informations nécessaires présentes
- **Clarté** : Descriptions compréhensibles
- **Précision** : Informations techniques correctes
- **Utilité** : Contenu actionnable pour techniciens

### Critères de Validation

- Procédure a au moins 2 steps
- Chaque step a un titre et des instructions
- Description de procédure > 50 caractères
- Tags pertinents présents
- Catégorie correcte

## Avantages de cette Approche

1. **Qualité maximale** : IA expert améliore chaque donnée
2. **Validation avant import** : Révision possible dans base locale
3. **Traçabilité** : Suivi complet du traitement
4. **Réversibilité** : Possibilité de corriger avant production
5. **Enrichissement progressif** : Plusieurs passes d'amélioration
6. **Gestion images** : Images analysées et associées intelligemment

## Fichiers à Créer

### Infrastructure

- `scripts/local_db/schema.sql`
- `scripts/local_db/db_manager.py`
- `scripts/local_db/init_db.py`

### Extraction Améliorée

- `scripts/extract_pdf_enhanced.py`
- `scripts/extract_images.py`
- `scripts/ocr_processor.py`

### Analyse IA

- `scripts/ai_analyzer.py`
- `scripts/prompts/expert_prompts.py`
- `scripts/vision_analyzer.py`

### Structuration

- `scripts/intelligent_structurer.py`
- `scripts/step_generator.py`
- `scripts/tip_extractor.py`

### Enrichissement

- `scripts/ai_enricher.py`
- `scripts/quality_validator.py`
- `scripts/content_optimizer.py`

### Validation

- `scripts/validator.py`
- `scripts/duplicate_detector.py`
- `scripts/quality_scorer.py`

### Import

- `scripts/migrate_to_production.py`
- `scripts/import_validator.py`

### Orchestration

- `scripts/intelligent_import.py` - Script principal orchestrant tout

## Ordre d'Exécution

1. **Setup** : Créer base locale SQLite
2. **Test sur 1 document** : Valider le pipeline complet
3. **Traitement par marque** : ABB → Huawei → Goodwe → etc.
4. **Révision** : Vérifier qualité dans base locale
5. **Import production** : Migrer données validées
6. **Génération embeddings** : Créer embeddings optimisés

## Métriques de Succès

- **Taux de traitement** : > 95% des documents traités
- **Qualité moyenne** : Score > 0.8/1.0
- **Complétude** : > 90% des procédures complètes
- **Enrichissement** : > 80% des procédures enrichies
- **Précision** : < 5% d'erreurs techniques