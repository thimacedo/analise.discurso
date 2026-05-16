-- PASA v47: Diferenciação de tipo de conteúdo (Post vs Reel)
ALTER TABLE public.comentarios
ADD COLUMN IF NOT EXISTS tipo_conteudo VARCHAR(20) DEFAULT 'POST';
