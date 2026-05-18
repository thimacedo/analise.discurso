-- PASA v48.2: Migrations Consolidadas (v44 -> v47)
-- COLE ESTE CÓDIGO INTEIRO NO SQL EDITOR DO SUPABASE DASHBOARD (WEB)

-- v44: Auditoria Anti-Alucinação
ALTER TABLE public.comentarios
ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS audit_discrepancy BOOLEAN DEFAULT FALSE;

-- v44: Métricas CCF
ALTER TABLE public.comentarios
ADD COLUMN IF NOT EXISTS ccf_density FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS ccf_sync FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS ccf_performativity FLOAT DEFAULT 0.0;

-- v47: Tipo de Conteúdo (Post vs Reel)
ALTER TABLE public.comentarios
ADD COLUMN IF NOT EXISTS tipo_conteudo VARCHAR(20) DEFAULT 'POST';

-- v46: Detecção de Shadowban
ALTER TABLE public.candidatos
ADD COLUMN IF NOT EXISTS shadowban_suspect BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS shadowban_detected_at TIMESTAMPTZ;
