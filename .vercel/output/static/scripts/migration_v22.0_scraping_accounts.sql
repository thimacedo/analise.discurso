-- MIGRATION V22.0 - SCRAPING ACCOUNTS & ROTATION
-- Sistema de gestão de identidades para resiliência de coleta

CREATE TABLE IF NOT EXISTS public.scraping_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    password TEXT,
    session_id TEXT,
    platform TEXT DEFAULT 'INSTAGRAM',
    status TEXT DEFAULT 'ACTIVE', -- ACTIVE, BLOCKED, COOLDOWN, SHADOWBANNED
    failures_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    cooldown_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Habilitar RLS se necessário, mas por enquanto mantemos service_role
ALTER TABLE public.scraping_accounts ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (Service Role Only)
CREATE POLICY "Service Role Access" ON public.scraping_accounts
    FOR ALL USING (true) WITH CHECK (true);

-- Gatilho de Update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_scraping_accounts_modtime
    BEFORE UPDATE ON public.scraping_accounts
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Inserir conta inicial do .env como fallback se necessário (via script python posterior)
