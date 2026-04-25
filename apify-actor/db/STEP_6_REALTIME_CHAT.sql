-- ==========================================================
-- INOVASYS - CHAT EM TEMPO REAL (v2.0)
-- Comunicação segura entre as partes e o árbitro
-- ==========================================================

CREATE TABLE IF NOT EXISTS public.mensagens_processo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    processo_id UUID REFERENCES public.processos(id) ON DELETE CASCADE,
    autor_id UUID REFERENCES auth.users(id),
    autor_nome TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.mensagens_processo ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Ver mensagens do processo" ON public.mensagens_processo
    FOR SELECT USING (
        processo_id IN (SELECT id FROM processos)
    );

CREATE POLICY "Qualquer autenticado pode enviar mensagem" ON public.mensagens_processo
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
