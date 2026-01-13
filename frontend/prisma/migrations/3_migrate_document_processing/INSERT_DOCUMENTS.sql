-- Migration SQL pour Supabase: Insertion des données document_processing
-- Ce script insère les 66 documents extraits depuis SQLite vers Supabase
-- À exécuter dans Supabase SQL Editor après avoir créé la table

-- IMPORTANT: Exécutez d'abord migration.sql pour créer la table

-- Insertion des documents (66 au total)
-- Note: Les IDs seront auto-générés par Supabase (SERIAL)

INSERT INTO "document_processing" (file_path, file_name, brand, file_type, file_size, status, extraction_data, created_at, updated_at)
VALUES
-- Les données seront insérées via l'API ou un script Python
-- car le contenu extraction_data peut être très volumineux
-- Ce fichier sert de référence pour la structure

-- Pour insérer les données, utilisez:
-- 1. L'API POST /api/admin/import-documents (si elle existe)
-- 2. Ou un script Python qui lit la base SQLite et insère dans Supabase

-- Exemple de structure pour un document:
('example_path', 'example.pdf', 'ABB', 'pdf', 1000000, 'extracted', '{"content": "..."}', NOW(), NOW())
ON CONFLICT (file_path) DO NOTHING;

-- Note: Les 66 documents sont actuellement dans la base SQLite locale
-- et doivent être migrés via un script Python qui:
-- 1. Lit depuis SQLite (via MCP sqlite)
-- 2. Insère dans Supabase (via API ou connexion directe PostgreSQL)
