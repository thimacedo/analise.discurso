-- Migração v28.0: Adiciona flags de mineração para processamento incremental
-- Descrição: Permite que o DataMiner saiba quais itens já foram processados tematicamente.

ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS mined boolean DEFAULT false;
ALTER TABLE public.anuncios ADD COLUMN IF NOT EXISTS mined boolean DEFAULT false;

-- Índices para acelerar a busca de itens não minerados
CREATE INDEX IF NOT EXISTS idx_comentarios_mined ON public.comentarios (mined) WHERE mined = false;
CREATE INDEX IF NOT EXISTS idx_anuncios_mined ON public.anuncios (mined) WHERE mined = false;

COMMENT ON COLUMN public.comentarios.mined IS 'Flag indicando se o comentário já passou pela mineração temática (NLP/Clustering)';
COMMENT ON COLUMN public.anuncios.mined IS 'Flag indicando se o anúncio já passou pela mineração temática (NLP/Clustering)';
