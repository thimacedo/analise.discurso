-- migrations/20260514_pasa_v17_audit_xp.sql
-- PASA v17: Audit and XP Ledger Infrastructure

-- 1. Tabela de Padrão Ouro (Auditoria Forense)
CREATE TABLE IF NOT EXISTS audit_gold_standards (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    original_comment_id UUID REFERENCES comentarios(id) ON DELETE SET NULL,
    texto_original TEXT NOT NULL,
    rotulo_correto VARCHAR(20) CHECK (rotulo_correto IN ('hate', 'not_hate')) NOT NULL,
    validado_por TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Tabela de Contabilidade de XP (Ledger)
CREATE TABLE IF NOT EXISTS worker_ledger (
    worker_name VARCHAR(50) PRIMARY KEY,
    current_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    total_runs INTEGER DEFAULT 0,
    total_critical_hits INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Alterações na tabela de runs para rastreabilidade
ALTER TABLE worker_runs
ADD COLUMN IF NOT EXISTS xp_gained INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS session_status VARCHAR(20) DEFAULT 'active';

-- 4. Trigger para atualizar o nível automaticamente no Ledger
CREATE OR REPLACE FUNCTION update_worker_level()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_xp >= 6000 THEN NEW.current_level := 5;
    ELSIF NEW.current_xp >= 3000 THEN NEW.current_level := 4;
    ELSIF NEW.current_xp >= 1500 THEN NEW.current_level := 3;
    ELSIF NEW.current_xp >= 500 THEN NEW.current_level := 2;
    ELSE NEW.current_level := 1;
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_level ON worker_ledger;
CREATE TRIGGER trigger_update_level
BEFORE UPDATE ON worker_ledger
FOR EACH ROW
EXECUTE FUNCTION update_worker_level();
