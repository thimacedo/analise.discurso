-- PASA v24: Tabela para gerenciamento de sessões ativas
CREATE TABLE IF NOT EXISTS public.worker_sessions (
    plataforma VARCHAR(50) PRIMARY KEY,
    cookies TEXT,
    status VARCHAR(20) DEFAULT 'active',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO public.worker_sessions (plataforma, status) VALUES ('instagram', 'active') ON CONFLICT (plataforma) DO NOTHING;
