-- Migration: Adição de campos PASA v16.4 para a tabela de anúncios
-- Diamond Edition v20.5.1

ALTER TABLE public.anuncios 
ADD COLUMN IF NOT EXISTS corpo_anuncio text,
ADD COLUMN IF NOT EXISTS categoria_ia text,
ADD COLUMN IF NOT EXISTS confianza_ia numeric(5,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS is_hate boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS processado_ia boolean DEFAULT false;

-- Index para facilitar busca de anúncios não processados
CREATE INDEX IF NOT EXISTS idx_anuncios_unprocessed ON public.anuncios (processado_ia) WHERE processado_ia = false;
