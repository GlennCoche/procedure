-- Script SQL pour insérer les 66 documents dans Supabase
-- À exécuter APRÈS avoir créé la table (migration.sql)

BEGIN;

-- IMPORTANT: Utilisez le script Python pour importer les données
-- python scripts/import_documents_to_supabase.py documents_export.json

-- Ou utilisez les données JSON exportées avec le script Python

COMMIT;
