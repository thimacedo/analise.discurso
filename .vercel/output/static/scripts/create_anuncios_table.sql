-- Tabela para armazenar anúncios da Meta Ad Library
CREATE TABLE IF NOT EXISTS public.anuncios (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    ad_id           text UNIQUE NOT NULL,
    candidato_id    text REFERENCES public.candidatos(username) ON DELETE CASCADE,
    page_name       text,
    status          text,
    paid_by         text,
    spend_range     text,
    ad_url          text,
    creative_body   text,
    data_coleta     timestamptz DEFAULT now(),
    created_at      timestamptz DEFAULT now()
);

-- Habilitar RLS
ALTER TABLE public.anuncios ENABLE ROW LEVEL SECURITY;

-- Políticas de acesso
DROP POLICY IF EXISTS "Anon pode ler anuncios" ON public.anuncios;
CREATE POLICY "Anon pode ler anuncios" ON public.anuncios FOR SELECT TO anon USING (true);

-- Index para performance
CREATE INDEX IF NOT EXISTS idx_anuncios_candidato ON public.anuncios (candidato_id);
CREATE INDEX IF NOT EXISTS idx_anuncios_ad_id ON public.anuncios (ad_id);
