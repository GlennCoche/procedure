# Instructions Finales - Migration vers Supabase

## ✅ Étape 1: Créer la table (CORRIGÉ)

**⚠️ ERREUR RENCONTRÉE**: Vous avez utilisé le schéma SQLite au lieu de PostgreSQL.

### Solution:

1. **Dans Supabase SQL Editor**, utilisez **UNIQUEMENT** ce fichier:
   ```
   frontend/prisma/migrations/3_migrate_document_processing/migration.sql
   ```

2. **NE PAS utiliser**:
   - ❌ `scripts/local_db/schema.sql` (c'est pour SQLite)
   - ❌ Tout autre fichier avec `AUTOINCREMENT`

3. **Le bon fichier contient**:
   ```sql
   CREATE TABLE IF NOT EXISTS "document_processing" (
       "id" SERIAL PRIMARY KEY,  -- ✅ SERIAL (PostgreSQL)
       ...
   );
   ```

4. **Copiez-collez** le contenu de `migration.sql` dans Supabase SQL Editor
5. **Cliquez sur "Run"**

## ✅ Étape 2: Importer les données

### Option A: Via Script Python (RECOMMANDÉ) 🚀

1. **Installer psycopg2**:
   ```bash
   pip install psycopg2-binary
   ```

2. **Configurer DATABASE_URL**:
   - Dans Supabase: Settings → Database → Connection string → URI
   - Copiez la connection string
   - Dans votre terminal:
     ```bash
     export DATABASE_URL="postgresql://postgres:[PASSWORD]@[PROJECT].supabase.co:5432/postgres"
     ```

3. **Les données sont déjà exportées**:
   - Fichier: `documents_export.json` (à créer avec toutes les données)
   - Ou utilisez directement les données depuis SQLite via MCP

4. **Exécuter le script**:
   ```bash
   python scripts/import_documents_to_supabase.py documents_export.json
   ```

### Option B: Via SQL direct (si vous préférez)

Les données sont trop volumineuses pour un script SQL manuel. Utilisez l'Option A.

## ✅ Étape 3: Vérifier la migration

Exécutez dans Supabase SQL Editor:

```sql
-- Compter par marque
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

**Résultat attendu**: 66 documents
- ABB: 9
- Delta: 16
- Goodwe: 18
- Huawei: 16
- Sungrow: 3
- Webdyn: 4

## 📝 Résumé des Fichiers

- ✅ `frontend/prisma/migrations/3_migrate_document_processing/migration.sql` - **À UTILISER** pour créer la table
- ✅ `scripts/import_documents_to_supabase.py` - Script Python pour importer les données
- ✅ `MIGRATION_GUIDE.md` - Guide complet avec troubleshooting
- ❌ `scripts/local_db/schema.sql` - **NE PAS UTILISER** (SQLite)

## 🎯 Checklist Finale

- [ ] Table créée dans Supabase (avec `migration.sql`)
- [ ] Vérification de la table réussie
- [ ] DATABASE_URL configuré
- [ ] Script Python exécuté
- [ ] 66 documents importés
- [ ] Vérification par marque réussie

## 🚀 Après la Migration

Une fois terminé:
1. Les données sont dans Supabase
2. Vous pouvez déployer sur Vercel
3. L'application pourra utiliser les documents
