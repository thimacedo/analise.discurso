-- Migration: Tabela de tokens de push para notificações FCM
-- v21.0

CREATE TABLE IF NOT EXISTS public.user_push_tokens (
    id           uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id      uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    token        text NOT NULL,
    device_id    text, -- ID opcional do dispositivo/navegador
    platform     text DEFAULT 'web', -- 'web', 'android', 'ios'
    created_at   timestamptz DEFAULT CURRENT_TIMESTAMP,
    updated_at   timestamptz DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, token)
);

ALTER TABLE public.user_push_tokens ENABLE ROW LEVEL SECURITY;

-- Usuários podem gerenciar seus próprios tokens
DROP POLICY IF EXISTS "Users can manage own tokens" ON public.user_push_tokens;
CREATE POLICY "Users can manage own tokens" 
ON public.user_push_tokens FOR ALL 
USING (auth.uid() = user_id);

-- Index para busca rápida por usuário
CREATE INDEX IF NOT EXISTS idx_push_tokens_user_id ON public.user_push_tokens (user_id);
