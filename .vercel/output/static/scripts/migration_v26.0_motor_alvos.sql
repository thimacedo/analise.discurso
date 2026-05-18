-- Migração STN-012: Motor de Inteligência de Alvos e Priorização

-- 1. Rastreio de Arquivos de Pesquisa
CREATE TABLE IF NOT EXISTS public.pesquisas_processadas (
    id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    arquivo     text NOT NULL UNIQUE,
    hash_sha256 text,
    data_leitura timestamptz DEFAULT CURRENT_TIMESTAMP,
    candidatos_detectados integer DEFAULT 0,
    status      text DEFAULT 'PROCESSADO' CHECK (status IN ('PROCESSADO', 'ERRO', 'IGNORADO'))
);

ALTER TABLE public.pesquisas_processadas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Serviços podem ler pesquisas" ON public.pesquisas_processadas FOR SELECT TO authenticated USING (true);

-- 2. Metadados de Priorização na tabela de candidatos
-- Nota: A tabela 'candidatos' já existe, vamos enriquecê-la.
ALTER TABLE public.candidatos 
ADD COLUMN IF NOT EXISTS nota_relevancia numeric(5,2) DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS ultima_pesquisa_id uuid REFERENCES public.pesquisas_processadas(id),
ADD COLUMN IF NOT EXISTS intenção_voto numeric(5,2) DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS prioridade_coleta integer DEFAULT 1; -- 1 (Baixa) a 5 (Crítica)

-- 3. Fila de Coleta Diária (Buffer para o orquestrador)
CREATE TABLE IF NOT EXISTS public.fila_coleta (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    candidato_id    text NOT NULL REFERENCES public.candidatos(username),
    prioridade      integer DEFAULT 1,
    status          text DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE', 'EM_CURSO', 'CONCLUIDO', 'FALHA')),
    tentativas      integer DEFAULT 0,
    data_agendada   date DEFAULT CURRENT_DATE,
    created_at      timestamptz DEFAULT CURRENT_TIMESTAMP,
    updated_at      timestamptz DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidato_id, data_agendada)
);

-- Index para performance do worker de raspagem
CREATE INDEX IF NOT EXISTS idx_fila_coleta_status_prioridade ON public.fila_coleta (status, prioridade DESC, data_agendada ASC);

-- 4. Função para calcular nota de recompensa do motor (Inteligência de Alvo)
-- Esta nota ajuda o motor a decidir quem vai para a fila
CREATE OR REPLACE FUNCTION public.calcular_prioridade_alvo(
    p_cargo text,
    p_intencao numeric
) RETURNS integer AS $$
DECLARE
    v_base integer := 1;
BEGIN
    -- Peso por Cargo
    IF p_cargo ILIKE '%Presidente%' THEN v_base := v_base + 3;
    ELSIF p_cargo ILIKE '%Governador%' THEN v_base := v_base + 2;
    ELSIF p_cargo ILIKE '%Senador%' THEN v_base := v_base + 1;
    END IF;

    -- Peso por Intenção de Voto
    IF p_intencao > 15 THEN v_base := v_base + 1; END IF;
    IF p_intencao > 30 THEN v_base := v_base + 1; END IF;

    RETURN LEAST(5, v_base);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
