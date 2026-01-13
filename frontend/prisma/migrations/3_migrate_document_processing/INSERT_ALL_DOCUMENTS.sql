-- Script SQL pour insérer les 65 documents dans Supabase
-- À exécuter APRÈS avoir créé la table (migration.sql)
-- 
-- IMPORTANT: Ce script utilise des INSERT avec ON CONFLICT pour éviter les doublons
-- Les données sont trop volumineuses pour être toutes incluses ici
-- Utilisez plutôt le script Python: python scripts/import_documents_to_supabase.py documents_export_complete.json

BEGIN;

-- Note: Les données complètes doivent être importées via le script Python
-- car certains extraction_data sont très volumineux (jusqu'à 138KB)

-- Exemple de structure INSERT (à répéter pour chaque document):
/*
INSERT INTO document_processing 
(file_path, file_name, brand, file_type, file_size, status, extraction_data, created_at, updated_at)
VALUES 
(
    '/Users/glenn/Desktop/procedures/docs/ABB/MES TRIO27.6.pdf',
    'MES TRIO27.6.pdf',
    'ABB',
    'pdf',
    400929,
    'extracted',
    '{"content_length": 1720, "title": "MES TRIO27.6.pdf", "topics": ["Réglages langue", "Câblage COM", "Aurora manager", "CosPhi", "Adresse modbus", "Seuil de tension"]}',
    '2026-01-13 21:54:13'::timestamp,
    '2026-01-13 21:54:13'::timestamp
)
ON CONFLICT (file_path) DO UPDATE SET
    file_name = EXCLUDED.file_name,
    brand = EXCLUDED.brand,
    file_type = EXCLUDED.file_type,
    file_size = EXCLUDED.file_size,
    status = EXCLUDED.status,
    extraction_data = EXCLUDED.extraction_data,
    updated_at = CURRENT_TIMESTAMP;
*/

-- Pour importer toutes les données, utilisez:
-- python scripts/import_documents_to_supabase.py documents_export_complete.json

COMMIT;
