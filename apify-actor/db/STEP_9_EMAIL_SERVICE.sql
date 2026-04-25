-- STEP 9: E-MAIL SERVICE 2.0
-- Cria a tabela para armazenar os templates de e-mail customizáveis.

CREATE TABLE IF NOT EXISTS public.email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE
);

-- Habilita RLS (Row Level Security)
ALTER TABLE public.email_templates ENABLE ROW LEVEL SECURITY;

-- Permissões
-- Admins podem gerenciar todos os templates de sua organização.
CREATE POLICY "Allow full access to organization admins"
ON public.email_templates
FOR ALL
TO authenticated
USING (
  (get_my_claim('org_role'::text)) = '"ADMIN"'::jsonb AND
  (get_my_claim('org_id'::text)) = organization_id::text::jsonb
)
WITH CHECK (
  (get_my_claim('org_role'::text)) = '"ADMIN"'::jsonb AND
  (get_my_claim('org_id'::text)) = organization_id::text::jsonb
);

-- Usuários autenticados podem ler templates.
CREATE POLICY "Allow read access to authenticated users"
ON public.email_templates
FOR SELECT
TO authenticated
USING (
  (get_my_claim('org_id'::text)) = organization_id::text::jsonb
);

-- Trigger para atualizar 'updated_at'
CREATE TRIGGER handle_updated_at
BEFORE UPDATE ON public.email_templates
FOR EACH ROW
EXECUTE PROCEDURE moddatetime (updated_at);
