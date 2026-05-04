-- Migration: Criação da tabela de alertas ativos
-- Diamond Edition v20.5.7

CREATE TABLE IF NOT EXISTS public.alertas_ativos (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tipo            text NOT NULL, -- 'PREDITIVO', 'SISTEMA', 'IA'
    severidade      text NOT NULL, -- 'BAIXA', 'MEDIA', 'ALTA', 'CRITICA'
    mensagem        text NOT NULL,
    metadados       jsonb DEFAULT '{}'::jsonb,
    lido            boolean DEFAULT false,
    created_at      timestamptz DEFAULT now()
);

-- Habilitar RLS
ALTER TABLE public.alertas_ativos ENABLE ROW LEVEL SECURITY;

-- Políticas
DROP POLICY IF EXISTS "Anon pode ler alertas" ON public.alertas_ativos;
CREATE POLICY "Anon pode ler alertas" ON public.alertas_ativos FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS "Service role pode tudo em alertas" ON public.alertas_ativos;
CREATE POLICY "Service role pode tudo em alertas" ON public.alertas_ativos FOR ALL TO service_role USING (true);

-- Index
CREATE INDEX IF NOT EXISTS idx_alertas_lido ON public.alertas_ativos (lido) WHERE lido = false;
CREATE INDEX IF NOT EXISTS idx_alertas_created ON public.alertas_ativos (created_at DESC);
