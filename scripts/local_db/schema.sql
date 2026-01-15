-- Schéma SQLite pour la base de données locale de validation
-- Ce schéma sera exécuté via le MCP sqlite

-- Table pour suivre le traitement des documents
CREATE TABLE IF NOT EXISTS document_processing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    brand TEXT,
    file_type TEXT,
    file_size INTEGER,
    status TEXT DEFAULT 'pending', -- 'pending', 'extracted', 'analyzed', 'structured', 'enriched', 'validated', 'imported', 'error'
    extraction_data TEXT, -- JSON avec texte brut, images, etc.
    analysis_data TEXT, -- JSON avec analyse IA
    structured_data TEXT, -- JSON avec procédures/steps générés
    enriched_data TEXT, -- JSON avec données enrichies
    validation_notes TEXT, -- Notes de validation
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les images extraites
CREATE TABLE IF NOT EXISTS document_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES document_processing(id) ON DELETE CASCADE,
    image_path TEXT,
    image_type TEXT, -- 'diagram', 'photo', 'graph', 'table'
    description TEXT, -- Description générée par Vision API
    extracted_text TEXT, -- Texte OCR si applicable
    page_number INTEGER,
    position_in_doc TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les procédures générées (local)
CREATE TABLE IF NOT EXISTS local_procedures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES document_processing(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    tags TEXT, -- JSON array
    steps TEXT, -- JSON array
    quality_score REAL DEFAULT 0.0, -- Score de qualité 0-1
    needs_review BOOLEAN DEFAULT 0,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les tips générés (local)
CREATE TABLE IF NOT EXISTS local_tips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES document_processing(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    tags TEXT, -- JSON array
    source_section TEXT, -- Section du document source
    quality_score REAL DEFAULT 0.0,
    needs_review BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour suivre les runs du pipeline séquentiel
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_dir TEXT NOT NULL,
    staging_dir TEXT NOT NULL,
    current_file TEXT,
    status TEXT DEFAULT 'idle', -- idle, running, paused, error, completed
    current_step TEXT,
    last_step TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de logs structurés par étape
CREATE TABLE IF NOT EXISTS pipeline_step_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    step TEXT NOT NULL,
    status TEXT NOT NULL,
    progress_current INTEGER DEFAULT 0,
    progress_total INTEGER DEFAULT 0,
    message TEXT,
    error TEXT,
    data_json TEXT,
    cpu_percent REAL DEFAULT 0.0,
    ram_mb REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_document_processing_status ON document_processing(status);
CREATE INDEX IF NOT EXISTS idx_document_processing_brand ON document_processing(brand);
CREATE INDEX IF NOT EXISTS idx_document_images_document_id ON document_images(document_id);
CREATE INDEX IF NOT EXISTS idx_local_procedures_document_id ON local_procedures(document_id);
CREATE INDEX IF NOT EXISTS idx_local_tips_document_id ON local_tips(document_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_step_logs_run_id ON pipeline_step_logs(run_id);
