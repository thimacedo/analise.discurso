-- Garante que a constraint única existe corretamente no id_externo para evitar duplicidade no UPSERT
-- PASA v49.4 - Correção de Sincronização e Duplicidade
ALTER TABLE public.comentarios DROP CONSTRAINT IF EXISTS comentarios_id_externo_key;
ALTER TABLE public.comentarios ADD CONSTRAINT comentarios_id_externo_key UNIQUE (id_externo);
