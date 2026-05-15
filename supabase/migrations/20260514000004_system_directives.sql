-- PASA v37: Tabela de Diretivas do Sistema (Auto-Evolução)
-- Permite controlar e atualizar o servidor local remotamente via Supabase
CREATE TABLE IF NOT EXISTS system_directives (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    command VARCHAR(50) NOT NULL, -- ex: 'UPDATE_REPO', 'RESTART', 'CHANGE_CONFIG'
    payload JSONB DEFAULT '{}',   -- ex: {"CYCLE_PAUSE": 600}
    executed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
