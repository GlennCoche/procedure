# Migration Document Processing vers Supabase

## Vue d'ensemble

Cette migration crée la table `document_processing` dans Supabase et prépare l'import des 66 documents extraits depuis SQLite.

## Étapes d'exécution

### 1. Créer la table dans Supabase

1. Connectez-vous à votre projet Supabase
2. Allez dans **SQL Editor**
3. Ouvrez le fichier `migration.sql`
4. **Copiez-collez le contenu** dans l'éditeur SQL
5. Cliquez sur **Run** (ou Cmd+Enter / Ctrl+Enter)
6. Vérifiez que la table a été créée avec succès

### 2. Vérifier la création de la table

Exécutez cette requête dans Supabase SQL Editor:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'document_processing';
```

Vous devriez voir `document_processing` dans les résultats.

### 3. Insérer les données

Les 66 documents sont actuellement dans la base SQLite locale. Pour les migrer vers Supabase, vous avez deux options:

#### Option A: Via l'API (recommandé)

Si une API `/api/admin/import-documents` existe, utilisez-la pour importer les documents.

#### Option B: Via script Python

Créez un script Python qui:
1. Lit les données depuis SQLite (via MCP sqlite)
2. Insère les données dans Supabase (via connexion PostgreSQL directe ou API)

Exemple de structure:

```python
import psycopg2
from supabase import create_client

# Connexion Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pour chaque document dans SQLite:
# supabase.table('document_processing').insert({
#     'file_path': doc['file_path'],
#     'file_name': doc['file_name'],
#     'brand': doc['brand'],
#     'file_type': doc['file_type'],
#     'status': doc['status'],
#     'extraction_data': doc['extraction_data']
# }).execute()
```

## Statistiques des documents

- **Total**: 66 documents
- **ABB**: 9 documents
- **Delta**: 16 documents  
- **Goodwe**: 18 documents
- **Huawei**: 16 documents
- **Sungrow**: 3 documents
- **Webdyn**: 4 documents

## Notes importantes

- Les données `extraction_data` peuvent être volumineuses (jusqu'à 138KB par document)
- La table utilise `file_path` comme UNIQUE constraint pour éviter les doublons
- Le statut par défaut est `'pending'`, mais tous les documents migrés ont le statut `'extracted'`

## Vérification post-migration

Après l'import, vérifiez le nombre de documents:

```sql
SELECT brand, COUNT(*) as count 
FROM document_processing 
WHERE status = 'extracted'
GROUP BY brand
ORDER BY brand;
```

Vous devriez voir 66 documents au total.
