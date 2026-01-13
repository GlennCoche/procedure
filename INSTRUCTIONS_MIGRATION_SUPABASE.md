# Instructions : Exécuter la Migration SQL sur Supabase

## Problème rencontré

L'erreur "EXPLAIN only works on a single SQL statement" apparaît si vous utilisez l'onglet "Explain" au lieu d'exécuter directement le SQL.

## Solution : Exécuter directement le SQL

### Étape 1 : Dans Supabase SQL Editor

1. **Assurez-vous d'être sur l'onglet "Results"** (pas "Explain")
2. **Sélectionnez tout le script SQL** (Cmd+A ou Ctrl+A)
3. **Cliquez sur le bouton "Run"** (ou appuyez sur Cmd+Enter / Ctrl+Enter)

### Étape 2 : Script SQL à exécuter

Copiez-collez ce script complet dans l'éditeur :

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

### Étape 3 : Exécuter

1. Cliquez sur **"Run"** (bouton en bas à droite, ou Cmd+Enter)
2. Attendez quelques secondes
3. Vous devriez voir "Success. No rows returned" ou un message de succès

### Étape 4 : Vérifier

Exécutez cette requête de vérification :

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
- 1 ligne pour l'extension `vector`
- 1 ligne pour la table `document_embeddings`
- 3 lignes pour les index (dont l'index vectoriel HNSW)

## Alternative : Exécuter statement par statement

Si vous préférez exécuter une instruction à la fois :

1. **Première instruction** :
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
→ Cliquez "Run"

2. **Deuxième instruction** :
```sql
CREATE TABLE IF NOT EXISTS "document_embeddings" (
    "id" SERIAL PRIMARY KEY,
    "document_type" VARCHAR(50) NOT NULL,
    "document_id" INTEGER NOT NULL,
    "content" TEXT NOT NULL,
    "embedding" vector(1536),
    "metadata" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
→ Cliquez "Run"

3. **Troisième instruction** (premier index) :
```sql
CREATE INDEX IF NOT EXISTS "document_embeddings_document_type_document_id_idx" 
ON "document_embeddings"("document_type", "document_id");
```
→ Cliquez "Run"

4. **Quatrième instruction** (deuxième index) :
```sql
CREATE INDEX IF NOT EXISTS "document_embeddings_document_type_idx" 
ON "document_embeddings"("document_type");
```
→ Cliquez "Run"

5. **Cinquième instruction** (index vectoriel) :
```sql
CREATE INDEX IF NOT EXISTS "document_embeddings_embedding_idx" 
ON "document_embeddings" 
USING hnsw (embedding vector_cosine_ops);
```
→ Cliquez "Run"

## Notes importantes

- **Ne pas utiliser "Explain"** : Cet onglet est pour analyser une seule requête SELECT
- **Utiliser "Run"** : Pour exécuter le script complet
- **L'extension vector** : Doit être activée avant de créer la table avec le type `vector`
- **Les index HNSW** : Peuvent prendre quelques secondes à créer sur une grande base

## En cas d'erreur

Si vous obtenez une erreur "extension vector does not exist" :
- Contactez le support Supabase pour activer l'extension
- Ou vérifiez que votre projet Supabase supporte pgvector

Si vous obtenez une erreur "relation already exists" :
- C'est normal si la table existe déjà
- Vous pouvez continuer, la migration est déjà appliquée
