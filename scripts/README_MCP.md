# Scripts d'Import Intelligent avec MCPs

Ce répertoire contient tous les scripts nécessaires pour l'import intelligent de documentation photovoltaïque en utilisant les MCPs (Model Context Protocol).

## Architecture avec MCPs

Le workflow utilise 4 MCPs principaux :

1. **pdf-tools** : Extraction PDF (texte, images, métadonnées)
2. **sqlite** : Gestion base de données locale (CRUD, requêtes)
3. **content-core** : Extraction intelligente et analyse IA
4. **faiss** : Stockage vectoriel et génération d'embeddings

## Workflow Complet

```
Document PDF
  ↓
[MCP: pdf-tools] → Extraction (texte, images, métadonnées)
  ↓
[MCP: sqlite] → Stockage brut (status: 'extracted')
  ↓
[MCP: content-core] → Analyse IA contextuelle
  ↓
[MCP: sqlite] → Stockage analyse (status: 'analyzed')
  ↓
[MCP: pdf-tools + OpenAI Vision] → Analyse images
  ↓
[MCP: content-core + sqlite] → Structuration (procédures/steps/tips)
  ↓
[MCP: content-core + sqlite] → Enrichissement
  ↓
[MCP: sqlite] → Validation qualité
  ↓
[MCP: sqlite + faiss] → Export et embeddings
  ↓
Import Supabase
```

## Scripts Disponibles

### Infrastructure

- **`local_db/schema.sql`** : Schéma SQLite pour la base locale
- **`local_db/db_manager.py`** : Gestionnaire de base de données (wrapper SQLite)
- **`local_db/init_db.py`** : Script d'initialisation de la base

### Extraction

- **`extract_pdf_enhanced.py`** : Extraction PDF améliorée avec pdf-tools MCP
- **`extract_images.py`** : Extraction d'images avec pdf-tools MCP

### Analyse

- **`ai_analyzer.py`** : Analyseur IA utilisant content-core MCP
- **`vision_analyzer.py`** : Analyseur d'images (pdf-tools + OpenAI Vision)
- **`prompts/expert_prompts.py`** : Prompts experts pour l'analyse

### Structuration et Enrichissement

- **`intelligent_structurer.py`** : Structurateur intelligent (content-core + sqlite)
- **`step_generator.py`** : Générateur de steps optimisé
- **`ai_enricher.py`** : Enrichisseur IA (content-core + sqlite)

### Validation

- **`validator.py`** : Validateur complet (sqlite)
- **`quality_validator.py`** : Calcul de scores de qualité

### Orchestration

- **`intelligent_import.py`** : Script principal d'orchestration
- **`mcp_helpers.py`** : Helpers pour documenter l'utilisation des MCPs

### Migration et Import

- **`migrate_to_production.py`** : Migration vers Supabase (sqlite)
- **`generate_embeddings.py`** : Génération d'embeddings (faiss)
- **`import_validated_data.py`** : Import final vers Supabase

### Tests

- **`test_pipeline.py`** : Test du pipeline complet
- **`process_all_documents.py`** : Traitement de tous les documents

## Utilisation des MCPs

### Pour l'Agent Cursor

L'agent Cursor doit utiliser directement les outils MCP à chaque étape :

#### Extraction
```python
# Utiliser pdf-tools MCP
pdf-tools.get_metadata(name="document.pdf")
pdf-tools.get_text_json(name="document.pdf")
pdf-tools.display_page_as_image(name="document.pdf", page_number=1)

# Utiliser content-core MCP (optionnel)
content-core.extract_content(file_path="/path/to/document.pdf")
```

#### Stockage
```python
# Utiliser sqlite MCP
sqlite.create_record(table="document_processing", data={...})
sqlite.update_records(table="document_processing", data={...}, conditions={...})
sqlite.read_records(table="local_procedures", conditions={...})
```

#### Analyse IA
```python
# Utiliser content-core MCP
content-core.extract_content(file_path="/path/to/document.pdf")
```

#### Validation
```python
# Utiliser sqlite MCP
sqlite.read_records(table="local_procedures")
sqlite.execute_sql(sql="SELECT ...", values=[...])
sqlite.update_records(table="local_procedures", data={...}, conditions={...})
```

#### Embeddings
```python
# Utiliser faiss MCP
faiss.ingest_document(document="text content", source="procedure_1")
faiss.query_rag_store(query="Comment installer un onduleur?", top_k=3)
```

## Structure de la Base Locale

La base SQLite locale contient 4 tables principales :

1. **`document_processing`** : Suivi du traitement des documents
2. **`document_images`** : Images extraites et analysées
3. **`local_procedures`** : Procédures générées (local)
4. **`local_tips`** : Tips générés (local)

## Workflow d'Exécution

### 1. Initialisation
```bash
python scripts/local_db/init_db.py
```

### 2. Traitement d'un Document
L'agent Cursor doit suivre le workflow défini dans `intelligent_import.py` :

1. Extraction (pdf-tools + content-core)
2. Analyse IA (content-core)
3. Analyse Vision (pdf-tools + OpenAI Vision)
4. Structuration (content-core + sqlite)
5. Enrichissement (content-core + sqlite)
6. Validation (sqlite)

### 3. Traitement de Tous les Documents
```bash
python scripts/process_all_documents.py
```

### 4. Migration vers Supabase
```bash
python scripts/migrate_to_production.py
python scripts/generate_embeddings.py
python scripts/import_validated_data.py
```

## Notes Importantes

1. **Utilisation des MCPs** : Les scripts documentent comment utiliser les MCPs. L'agent Cursor doit utiliser directement les outils MCP, pas les wrappers Python.

2. **Content-core** : Utilise OpenAI en interne, l'API key est déjà configurée dans le MCP.

3. **Faiss** : Pour la génération d'embeddings, utiliser le MCP faiss qui gère le stockage vectoriel local.

4. **SQLite** : Toutes les opérations de base de données passent par le MCP sqlite pour garantir la cohérence.

5. **PDF-tools** : Utilisé pour l'extraction spécialisée PDF (texte, images, métadonnées).

## Métriques de Succès

- **Taux de traitement** : > 95% des documents traités
- **Qualité moyenne** : Score > 0.8/1.0
- **Complétude** : > 90% des procédures complètes
- **Enrichissement** : > 80% des procédures enrichies
- **Précision** : < 5% d'erreurs techniques
