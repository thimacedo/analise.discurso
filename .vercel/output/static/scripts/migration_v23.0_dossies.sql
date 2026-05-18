-- Migration: Repositório de Dossiês Forenses
-- Diamond Edition v20.5.2

CREATE TABLE IF NOT EXISTS public.dossies (
    id                uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    candidato_id      text REFERENCES public.candidatos(username) NOT NULL,
    data_geracao      timestamptz DEFAULT CURRENT_TIMESTAMP,
    hash_integridade  text NOT NULL, -- SHA-256 do conjunto de dados periciado
    total_comentarios integer DEFAULT 0,
    total_hate        integer DEFAULT 0,
    versao_pasa       text DEFAULT 'v16.4',
    arquivo_path      text, -- Caminho relativo para o arquivo PDF gerado
    created_at        timestamptz DEFAULT CURRENT_TIMESTAMP,
    updated_at        timestamptz DEFAULT CURRENT_TIMESTAMP
);

-- Ativar RLS
ALTER TABLE public.dossies ENABLE ROW LEVEL SECURITY;

-- Políticas de Acesso
DROP POLICY IF EXISTS "Anon pode ler dossies" ON public.dossies;
CREATE POLICY "Anon pode ler dossies" ON public.dossies FOR SELECT TO anon USING (true);

-- Índices para performance forense
CREATE INDEX IF NOT EXISTS idx_dossies_candidato ON public.dossies (candidato_id);
CREATE INDEX IF NOT EXISTS idx_dossies_hash ON public.dossies (hash_integridade);
CREATE INDEX IF NOT EXISTS idx_dossies_data ON public.dossies (data_geracao DESC);

-- Trigger para atualizar o timestamp de updated_at
CREATE OR REPLACE FUNCTION update_dossie_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER tr_update_dossie_updated_at
    BEFORE UPDATE ON public.dossies
    FOR EACH ROW
    EXECUTE FUNCTION update_dossie_updated_at();
