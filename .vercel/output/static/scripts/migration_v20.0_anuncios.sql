-- Migration: Criação da tabela de anúncios da Meta Ad Library
-- Diamond Edition v20.0

CREATE TABLE IF NOT EXISTS public.anuncios (
    id           uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    ad_id        text UNIQUE NOT NULL, -- ID do anúncio na Meta
    candidato_id text REFERENCES public.candidatos(username),
    pagador      text, -- "Paid by"
    valor_min    numeric(12,2),
    valor_max    numeric(12,2),
    moeda        text DEFAULT 'BRL',
    data_inicio  date,
    data_fim     date,
    status       text, -- 'active', 'inactive'
    alcance_min  integer,
    alcance_max  integer,
    criativo_url text,
    page_name    text,
    created_at   timestamptz DEFAULT CURRENT_TIMESTAMP,
    updated_at   timestamptz DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.anuncios ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Anon pode ler anuncios" ON public.anuncios;
CREATE POLICY "Anon pode ler anuncios" ON public.anuncios FOR SELECT TO anon USING (true);

-- Index para busca rápida por candidato
CREATE INDEX IF NOT EXISTS idx_anuncios_candidato ON public.anuncios (candidato_id);
CREATE INDEX IF NOT EXISTS idx_anuncios_ad_id ON public.anuncios (ad_id);
