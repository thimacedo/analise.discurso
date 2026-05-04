-- Migration: Infraestrutura Multi-Tenancy
-- Diamond Edition v20.5.9

-- 1. Tabela de Organizações
CREATE TABLE IF NOT EXISTS public.organizations (
    id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    name        text NOT NULL,
    slug        text UNIQUE NOT NULL,
    plan        text DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    created_at  timestamptz DEFAULT now(),
    updated_at  timestamptz DEFAULT now()
);

-- 2. Tabela de Membros (Vincula Perfis a Organizações)
CREATE TABLE IF NOT EXISTS public.organization_members (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id uuid REFERENCES public.organizations(id) ON DELETE CASCADE,
    profile_id      uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    role            text DEFAULT 'member', -- 'owner', 'admin', 'member'
    created_at      timestamptz DEFAULT now(),
    UNIQUE(organization_id, profile_id)
);

-- 3. Adicionar organization_id nas tabelas core
ALTER TABLE public.candidatos ADD COLUMN IF NOT EXISTS organization_id uuid REFERENCES public.organizations(id);
ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS organization_id uuid REFERENCES public.organizations(id);
ALTER TABLE public.anuncios ADD COLUMN IF NOT EXISTS organization_id uuid REFERENCES public.organizations(id);
ALTER TABLE public.alertas_ativos ADD COLUMN IF NOT EXISTS organization_id uuid REFERENCES public.organizations(id);
ALTER TABLE public.dossies ADD COLUMN IF NOT EXISTS organization_id uuid REFERENCES public.organizations(id);

-- 4. Habilitar RLS e Políticas Multi-Tenancy
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;

-- Política: Usuários só veem organizações das quais são membros
DROP POLICY IF EXISTS "Users can see their own organizations" ON public.organizations;
CREATE POLICY "Users can see their own organizations" ON public.organizations
    FOR SELECT TO authenticated
    USING (id IN (SELECT organization_id FROM public.organization_members WHERE profile_id = auth.uid()));

-- Política Genérica para tabelas core: Filtrar por organization_id do usuário
-- Nota: Para simplificar, usaremos uma função auxiliar no futuro, mas aqui vai a base
DROP POLICY IF EXISTS "Tenant isolation for candidatos" ON public.candidatos;
CREATE POLICY "Tenant isolation for candidatos" ON public.candidatos
    FOR ALL TO authenticated
    USING (organization_id IN (SELECT organization_id FROM public.organization_members WHERE profile_id = auth.uid()));

-- Index para performance de busca por tenant
CREATE INDEX IF NOT EXISTS idx_candidatos_org ON public.candidatos(organization_id);
CREATE INDEX IF NOT EXISTS idx_comentarios_org ON public.comentarios(organization_id);
CREATE INDEX IF NOT EXISTS idx_anuncios_org ON public.anuncios(organization_id);
