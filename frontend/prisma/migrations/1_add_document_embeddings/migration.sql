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
CREATE INDEX IF NOT EXISTS "document_embeddings_document_type_document_id_idx" ON "document_embeddings"("document_type", "document_id");
CREATE INDEX IF NOT EXISTS "document_embeddings_document_type_idx" ON "document_embeddings"("document_type");

-- Create vector index for similarity search (using HNSW for better performance)
CREATE INDEX IF NOT EXISTS "document_embeddings_embedding_idx" ON "document_embeddings" 
USING hnsw (embedding vector_cosine_ops);
