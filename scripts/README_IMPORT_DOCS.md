# Guide d'Import de Documentation Technique

Ce guide explique comment utiliser le système d'import pour extraire et importer automatiquement les documents techniques du dossier `docs/` dans la base de données.

## Vue d'ensemble

Le système d'import comprend plusieurs scripts qui travaillent ensemble :

1. **`inventory_docs.py`** - Inventaire des documents
2. **`extract_pdf.py`** - Extraction de contenu depuis les PDFs
3. **`extract_mms.py`** - Extraction de contenu depuis les fichiers MMS
4. **`structure_document.py`** - Structuration en procédures et steps
5. **`import_documents.py`** - Import principal dans la base de données
6. **`generate_embeddings.py`** - Génération d'embeddings pour recherche vectorielle

## Prérequis

### Installation des dépendances

```bash
cd backend
pip install -r requirements.txt
```

Les dépendances nécessaires sont :
- `pdfplumber` - Extraction PDF
- `pymupdf` - Alternative extraction PDF
- `python-docx` - Extraction DOCX
- `openai` - Génération d'embeddings
- `pgvector` - Support vectoriel PostgreSQL
- `tqdm` - Barres de progression

### Configuration

1. **Variables d'environnement** :
   - `OPENAI_API_KEY` : Clé API OpenAI pour les embeddings
   - `DATABASE_URL` : URL de connexion à la base de données

2. **Base de données** :
   - L'extension `pgvector` doit être activée sur Supabase
   - La table `document_embeddings` doit être créée (migration incluse)

## Utilisation

### Étape 1 : Inventaire des documents

Créer un inventaire de tous les documents :

```bash
python3 scripts/inventory_docs.py
```

Cela génère :
- `scripts/inventory_output/inventory.json` - Inventaire complet
- `scripts/inventory_output/inventory.csv` - Format CSV
- `scripts/inventory_output/summary.json` - Résumé par marque/type

### Étape 2 : Import par marque

Importer les documents d'une marque spécifique :

```bash
# Importer ABB
python3 scripts/import_documents.py \
  --brand ABB \
  --api-url http://localhost:8000 \
  --email admin@procedures.local \
  --password admin123

# Importer toutes les marques
python3 scripts/import_documents.py \
  --all \
  --api-url http://localhost:8000 \
  --email admin@procedures.local \
  --password admin123
```

### Étape 3 : Génération des embeddings

Générer les embeddings pour la recherche vectorielle :

```bash
python3 scripts/generate_embeddings.py \
  --api-url http://localhost:8000 \
  --openai-key YOUR_OPENAI_KEY
```

Ou utiliser la variable d'environnement :

```bash
export OPENAI_API_KEY=your_key_here
python3 scripts/generate_embeddings.py --api-url http://localhost:8000
```

## Ordre d'import recommandé

1. **ABB** (11 PDFs) - Test initial
2. **Huawei** (19 fichiers) - Déjà partiellement traité
3. **Goodwe** (20 PDFs)
4. **Sungrow** (2 PDFs)
5. **Webdynsun/WebdynsunPM** (8 fichiers)
6. **Delta** (701 fichiers) - Le plus volumineux
7. **Bridage Raccordement** (2 PDFs)

## Structure des données créées

### Procédures

Chaque section de document devient une procédure avec :
- **Titre** : Titre de la section
- **Description** : Contenu de la section
- **Catégorie** : "Marque - Type" (ex: "ABB - Installation")
- **Tags** : [marque, type, mots-clés]
- **Steps** : Étapes extraites depuis le contenu

### Tips

Conseils pratiques extraits automatiquement :
- Phrases contenant "conseil", "astuce", "attention", etc.
- Références rapides
- Astuces de dépannage

## Recherche vectorielle

Une fois les embeddings générés, le Chat IA utilise automatiquement la recherche vectorielle pour enrichir le contexte avec les procédures et tips pertinents.

## Dépannage

### Erreur d'extraction PDF

- Vérifier que `pdfplumber` ou `pymupdf` est installé
- Certains PDFs scannés nécessitent OCR (non implémenté actuellement)

### Erreur d'import

- Vérifier que l'API backend est démarrée
- Vérifier les identifiants admin
- Vérifier que l'utilisateur a le rôle "admin"

### Erreur d'embeddings

- Vérifier que `OPENAI_API_KEY` est configuré
- Vérifier les limites de taux OpenAI
- Les embeddings sont sauvegardés dans `scripts/embeddings_output/` pour import manuel si nécessaire

## Fichiers générés

- `scripts/inventory_output/` - Inventaires
- `scripts/embeddings_output/` - Embeddings générés (JSON)

## Notes

- Les fichiers déjà traités sont détectés par hash MD5 pour éviter les doublons
- Le système gère automatiquement les erreurs et continue le traitement
- Les logs détaillés sont affichés dans la console
