-- supabase/migrations/20260516000001_add_confidence_and_evidence.sql

ALTER TABLE comentarios
ADD COLUMN IF NOT EXISTS confidence_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS evidence_extracted TEXT;