-- Migration: Import document_processing data from SQLite to Supabase
-- This script creates a temporary table to store extracted document data
-- The data will later be processed to create Procedures and Tips

-- Create document_processing table for staging extracted documents
CREATE TABLE IF NOT EXISTS "document_processing" (
    "id" SERIAL PRIMARY KEY,
    "file_path" TEXT UNIQUE NOT NULL,
    "file_name" TEXT NOT NULL,
    "brand" VARCHAR(100),
    "file_type" VARCHAR(50),
    "file_size" INTEGER,
    "status" VARCHAR(50) DEFAULT 'pending',
    "extraction_data" TEXT,
    "analysis_data" TEXT,
    "structured_data" TEXT,
    "enriched_data" TEXT,
    "validation_notes" TEXT,
    "error_message" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS "document_processing_brand_idx" ON "document_processing"("brand");
CREATE INDEX IF NOT EXISTS "document_processing_status_idx" ON "document_processing"("status");
CREATE INDEX IF NOT EXISTS "document_processing_file_type_idx" ON "document_processing"("file_type");

-- Note: The actual data insertion will be done via a Python script or manual SQL
-- This migration only creates the table structure
