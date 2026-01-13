# Guide Complet de Migration vers Supabase

## 🎯 Objectif

Migrer les **66 documents** extraits depuis SQLite vers Supabase PostgreSQL.

## 📋 Étapes de Migration

### Étape 1: Créer la table dans Supabase ✅

1. **Connectez-vous à Supabase**: https://supabase.com/dashboard
2. **Allez dans SQL Editor**
3. **Ouvrez le fichier**: `frontend/prisma/migrations/3_migrate_document_processing/migration.sql`
4. **Copiez-collez le contenu** dans l'éditeur SQL
5. **⚠️ IMPORTANT**: Assurez-vous d'utiliser le fichier `migration.sql` (PostgreSQL), **PAS** `schema.sql` (SQLite)
6. **Cliquez sur "Run"** (ou Cmd+Enter / Ctrl+Enter)

**Le fichier correct contient:**
```sql
CREATE TABLE IF NOT EXISTS "document_processing" (
    "id" SERIAL PRIMARY KEY,  -- ✅ SERIAL (PostgreSQL)
    ...
);
```

**❌ NE PAS utiliser:**
```sql
CREATE TABLE IF NOT EXISTS document_processing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ❌ AUTOINCREMENT (SQLite)
    ...
);
```

### Étape 2: Vérifier la création de la table

Exécutez dans Supabase SQL Editor:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'document_processing';
```

Vous devriez voir `document_processing` dans les résultats.

### Étape 3: Exporter les données depuis SQLite

Les données sont dans SQLite. Vous avez **3 options** pour les migrer:

#### Option A: Via Script Python (Recommandé) 🚀

1. **Exporter les données depuis SQLite** (via MCP dans Cursor):
   - Utilisez `mcp_sqlite_query` avec:
   ```sql
   SELECT * FROM document_processing WHERE status = 'extracted'
   ```
   - Sauvegardez les résultats en JSON

2. **Configurer DATABASE_URL**:
   ```bash
   # Dans .env ou export
   export DATABASE_URL="postgresql://postgres:[PASSWORD]@[PROJECT].supabase.co:5432/postgres"
   ```
   
   Trouvez votre DATABASE_URL dans Supabase:
   - Settings → Database → Connection string → URI

3. **Installer psycopg2**:
   ```bash
   pip install psycopg2-binary
   ```

4. **Exécuter le script d'import**:
   ```bash
   python scripts/import_documents_to_supabase.py documents_export.json
   ```

#### Option B: Via SQL généré manuellement

1. **Générer le script SQL** avec les INSERT statements
2. **Exécuter dans Supabase SQL Editor**

#### Option C: Via API REST (si disponible)

Si vous avez une API `/api/admin/import-documents`, utilisez-la.

### Étape 4: Vérifier la migration

Exécutez dans Supabase SQL Editor:

```sql
-- Compter les documents par marque
SELECT brand, COUNT(*) as count 
FROM document_processing 
WHERE status = 'extracted'
GROUP BY brand
ORDER BY brand;

-- Total
SELECT COUNT(*) as total 
FROM document_processing 
WHERE status = 'extracted';
```

Vous devriez voir **66 documents** au total:
- ABB: 9
- Delta: 16
- Goodwe: 18
- Huawei: 16
- Sungrow: 3
- Webdyn: 4

## 🔧 Résolution de Problèmes

### Erreur: "syntax error at or near AUTOINCREMENT"

**Cause**: Vous avez utilisé le schéma SQLite au lieu de PostgreSQL.

**Solution**: 
- Utilisez `frontend/prisma/migrations/3_migrate_document_processing/migration.sql`
- **PAS** `scripts/local_db/schema.sql`

### Erreur: "relation document_processing does not exist"

**Cause**: La table n'a pas été créée.

**Solution**: Exécutez d'abord `migration.sql` dans Supabase SQL Editor.

### Erreur de connexion PostgreSQL

**Cause**: DATABASE_URL incorrect ou credentials invalides.

**Solution**: 
- Vérifiez votre DATABASE_URL dans Supabase Settings
- Format: `postgresql://postgres:password@host:port/dbname`

## 📊 Statistiques Attendues

Après migration réussie:
- **Total documents**: 66
- **Statut**: `extracted`
- **Marques**: 6 (ABB, Delta, Goodwe, Huawei, Sungrow, Webdyn)

## ✅ Checklist de Migration

- [ ] Table `document_processing` créée dans Supabase
- [ ] Vérification de la table réussie
- [ ] Données exportées depuis SQLite
- [ ] Données importées dans Supabase
- [ ] Vérification du nombre de documents (66)
- [ ] Vérification par marque

## 🚀 Après la Migration

Une fois les données migrées, vous pouvez:
1. **Déployer sur Vercel** (les migrations seront appliquées automatiquement)
2. **Utiliser les données** dans l'application
3. **Créer des Procedures/Tips** à partir des documents extraits
