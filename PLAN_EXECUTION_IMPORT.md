# Plan d'Exécution - Import de Documentation Technique

Ce plan détaille les étapes pour installer, configurer et exécuter le système d'import de documentation.

## 📋 Vue d'ensemble

**Objectif** : Importer automatiquement les 763 fichiers techniques du dossier `docs/` dans la base de données pour alimenter les procédures, tips et enrichir le Chat IA.

**Durée estimée** : 2-3 heures (selon le nombre de documents)

---

## Étape 1 : Installation des Dépendances Python

### 1.1 Vérifier l'environnement Python

```bash
# Vérifier la version Python (3.8+ requis)
python3 --version

# Vérifier si pip est installé
python3 -m pip --version
```

### 1.2 Activer l'environnement virtuel (si existant)

```bash
cd /Users/glenn/Desktop/procedures/backend

# Si un venv existe déjà
source venv/bin/activate  # Sur macOS/Linux
# OU
venv\Scripts\activate  # Sur Windows
```

### 1.3 Installer les dépendances

```bash
# Depuis le dossier backend
cd /Users/glenn/Desktop/procedures/backend

# Installer toutes les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list | grep -E "(pdfplumber|pymupdf|openai|pgvector|tqdm)"
```

**Dépendances à installer** :
- `pdfplumber==0.10.3` - Extraction PDF
- `pymupdf==1.23.8` - Alternative extraction PDF
- `python-docx==1.1.0` - Extraction DOCX
- `pgvector==0.2.4` - Support vectoriel PostgreSQL
- `psycopg2-binary==2.9.9` - Driver PostgreSQL
- `sentence-transformers==2.3.1` - Embeddings locaux (optionnel)
- `tqdm==4.66.1` - Barres de progression

**Vérification** :
```bash
python3 -c "import pdfplumber; import fitz; import openai; print('✅ Toutes les dépendances sont installées')"
```

---

## Étape 2 : Appliquer la Migration SQL sur Supabase

### 2.1 Accéder à Supabase SQL Editor

1. Aller sur : https://supabase.com/dashboard/project/[VOTRE_PROJECT_ID]/sql/new
2. Ou via : Dashboard → SQL Editor → New Query

### 2.2 Copier et exécuter la migration

Copier le contenu du fichier `frontend/prisma/migrations/1_add_document_embeddings/migration.sql` :

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create document_embeddings table
CREATE TABLE IF NOT EXISTS "document_embeddings" (
    "id" SERIAL PRIMARY KEY,
    "document_type" VARCHAR(50) NOT NULL,
    "document_id" INTEGER NOT NULL,
    "content" TEXT NOT NULL,
    "embedding" vector(1536),
    "metadata" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS "document_embeddings_document_type_document_id_idx" 
ON "document_embeddings"("document_type", "document_id");

CREATE INDEX IF NOT EXISTS "document_embeddings_document_type_idx" 
ON "document_embeddings"("document_type");

-- Create vector index for similarity search (using HNSW for better performance)
CREATE INDEX IF NOT EXISTS "document_embeddings_embedding_idx" 
ON "document_embeddings" 
USING hnsw (embedding vector_cosine_ops);
```

### 2.3 Vérifier l'application

Exécuter cette requête pour vérifier :

```sql
-- Vérifier que l'extension est activée
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Vérifier que la table existe
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'document_embeddings';

-- Vérifier les index
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'document_embeddings';
```

**Résultat attendu** :
- Extension `vector` activée
- Table `document_embeddings` créée
- 3 index créés (dont l'index vectoriel HNSW)

### 2.4 Alternative : Via Prisma Migrate (si préféré)

```bash
cd /Users/glenn/Desktop/procedures/frontend

# S'assurer que DATABASE_URL est configuré dans .env.local
# Puis appliquer la migration
npx prisma migrate deploy
```

---

## Étape 3 : Lancer l'Inventaire des Documents

### 3.1 Exécuter le script d'inventaire

```bash
cd /Users/glenn/Desktop/procedures

# Lancer l'inventaire
python3 scripts/inventory_docs.py
```

### 3.2 Vérifier les résultats

Le script génère 3 fichiers dans `scripts/inventory_output/` :

```bash
# Voir le résumé
cat scripts/inventory_output/summary.json | python3 -m json.tool

# Voir les statistiques par marque
python3 -c "
import json
with open('scripts/inventory_output/summary.json') as f:
    data = json.load(f)
    print('📊 Résumé par marque:')
    for brand, info in data['by_brand'].items():
        print(f'  {brand}: {info[\"count\"]} fichiers ({info[\"size_mb\"]} MB)')
"
```

**Résultat attendu** :
- ABB : ~11 fichiers
- Delta : ~701 fichiers
- Goodwe : ~20 fichiers
- Huawei : ~19 fichiers
- Sungrow : ~2 fichiers
- Webdynsun : ~4 fichiers
- WebdynsunPM : ~4 fichiers
- Bridage Raccordement : ~2 fichiers

---

## Étape 4 : Importer une Marque (Test avec ABB)

### 4.1 Prérequis

- Backend API démarré sur `http://localhost:8000`
- Utilisateur admin créé (email et mot de passe requis)

### 4.2 Vérifier que le backend est démarré

```bash
# Tester la connexion API
curl http://localhost:8000/api/health

# Ou ouvrir dans le navigateur
open http://localhost:8000/docs
```

### 4.3 Importer la marque ABB

```bash
cd /Users/glenn/Desktop/procedures

# Importer ABB (11 PDFs - bon pour tester)
python3 scripts/import_documents.py \
  --brand ABB \
  --api-url http://localhost:8000 \
  --email admin@procedures.local \
  --password admin123
```

**Remplacez** :
- `admin@procedures.local` par votre email admin
- `admin123` par votre mot de passe admin

### 4.4 Vérifier l'import

```bash
# Vérifier via l'API
curl http://localhost:8000/api/procedures?category=ABB

# Ou compter les procédures créées
curl http://localhost:8000/api/procedures | python3 -c "
import sys, json
data = json.load(sys.stdin)
abb_procs = [p for p in data if 'ABB' in p.get('category', '')]
print(f'✅ {len(abb_procs)} procédures ABB créées')
"
```

### 4.5 Importer d'autres marques (optionnel)

```bash
# Importer toutes les marques (long processus)
python3 scripts/import_documents.py \
  --all \
  --api-url http://localhost:8000 \
  --email admin@procedures.local \
  --password admin123
```

**Ordre recommandé** :
1. ABB (11 PDFs) - Test initial ✅
2. Huawei (19 fichiers)
3. Goodwe (20 PDFs)
4. Sungrow (2 PDFs)
5. Webdynsun/WebdynsunPM (8 fichiers)
6. Delta (701 fichiers) - Le plus volumineux
7. Bridage Raccordement (2 PDFs)

---

## Étape 5 : Générer les Embeddings

### 5.1 Prérequis

- Clé API OpenAI configurée
- Procédures et tips importés dans la base de données

### 5.2 Configurer la clé OpenAI

**Option A : Variable d'environnement (recommandé)**

```bash
export OPENAI_API_KEY="sk-..."
```

**Option B : Argument de ligne de commande**

```bash
python3 scripts/generate_embeddings.py --openai-key "sk-..."
```

### 5.3 Générer les embeddings

```bash
cd /Users/glenn/Desktop/procedures

# Générer pour toutes les procédures et tips
python3 scripts/generate_embeddings.py \
  --api-url http://localhost:8000 \
  --openai-key $OPENAI_API_KEY

# OU si la variable d'environnement est configurée
python3 scripts/generate_embeddings.py --api-url http://localhost:8000
```

**Options disponibles** :
```bash
# Générer uniquement pour les procédures
python3 scripts/generate_embeddings.py --procedures-only

# Générer uniquement pour les tips
python3 scripts/generate_embeddings.py --tips-only

# Limiter le nombre (pour test)
python3 scripts/generate_embeddings.py --limit 10
```

### 5.4 Vérifier la génération

```bash
# Vérifier dans Supabase SQL Editor
SELECT 
  document_type,
  COUNT(*) as count,
  COUNT(embedding) as with_embedding
FROM document_embeddings
GROUP BY document_type;
```

**Résultat attendu** :
- `procedure` : X embeddings générés
- `tip` : Y embeddings générés

### 5.5 Import manuel des embeddings (si nécessaire)

Si le script sauvegarde dans `scripts/embeddings_output/`, vous pouvez les importer manuellement :

```sql
-- Exemple d'import depuis un fichier JSON
-- (Adapter selon le format généré)
INSERT INTO document_embeddings (document_type, document_id, content, embedding, metadata)
VALUES (
  'procedure',
  1,
  'Contenu...',
  '[0.1, 0.2, ...]'::vector,
  '{"title": "..."}'::jsonb
);
```

---

## Vérification Finale

### Tester le Chat IA enrichi

1. Démarrer le frontend : `cd frontend && npm run dev`
2. Ouvrir : http://localhost:3000
3. Se connecter
4. Tester le Chat IA avec une question technique
5. Vérifier que le contexte enrichi est utilisé

### Vérifier la recherche vectorielle

```bash
# Tester via l'API (si endpoint créé)
curl -X POST http://localhost:8000/api/vector-search \
  -H "Content-Type: application/json" \
  -d '{"query": "configuration onduleur ABB"}'
```

---

## Dépannage

### Erreur : Module non trouvé

```bash
# Réinstaller les dépendances
pip install --upgrade -r backend/requirements.txt
```

### Erreur : Extension vector non disponible

```sql
-- Vérifier dans Supabase
SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Si non disponible, contacter le support Supabase
```

### Erreur : Authentification API échouée

- Vérifier que le backend est démarré
- Vérifier les identifiants admin
- Vérifier que l'utilisateur a le rôle "admin"

### Erreur : Limite de taux OpenAI

- Attendre quelques minutes
- Utiliser `--limit` pour traiter par petits lots
- Vérifier les quotas sur https://platform.openai.com/usage

---

## Prochaines Étapes

Une fois l'import terminé :

1. ✅ Vérifier la qualité des procédures créées
2. ✅ Tester le Chat IA avec différentes questions
3. ✅ Ajuster les paramètres de recherche vectorielle si nécessaire
4. ✅ Ajouter plus de documents si besoin
5. ✅ Monitorer l'utilisation et les performances

---

## Notes Importantes

- **Coûts OpenAI** : La génération d'embeddings utilise `text-embedding-3-small` (modèle économique)
- **Performance** : L'index HNSW permet des recherches rapides même avec beaucoup de documents
- **Doublons** : Le système détecte automatiquement les fichiers déjà traités (hash MD5)
- **Logs** : Tous les scripts affichent des logs détaillés pour le suivi

---

## Support

En cas de problème :
1. Vérifier les logs des scripts
2. Vérifier les logs du backend (console)
3. Vérifier les logs Supabase (Dashboard → Logs)
4. Consulter `scripts/README_IMPORT_DOCS.md` pour plus de détails
