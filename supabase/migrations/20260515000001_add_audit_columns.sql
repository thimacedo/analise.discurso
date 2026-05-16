-- PASA v44.3: Colunas para rastreabilidade da Auditoria Cruzada
ALTER TABLE public.comentarios
ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS audit_discrepancy BOOLEAN DEFAULT FALSE;
