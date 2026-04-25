-- ROADMAP: Sentinela Democrática
-- Objetivo: Monitoramento de redes sociais para análise de narrativas e engajamento.

-- 1. perfis: Armazena dados de atores políticos e influenciadores.
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    full_name TEXT,
    bio TEXT,
    is_political_actor BOOLEAN DEFAULT false,
    platform_id TEXT UNIQUE NOT NULL, -- ID original da plataforma
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. posts: Armazena o conteúdo extraído.
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id),
    post_url TEXT UNIQUE NOT NULL,
    caption TEXT,
    media_type TEXT, -- 'image', 'video', 'carousel'
    platform_id TEXT UNIQUE NOT NULL, -- ID do post na plataforma
    posted_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. engagement_history: Registros de métricas de engajamento ao longo do tempo.
CREATE TABLE engagement_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id),
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    tracked_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. narratives: Classificação e análise de narrativas.
CREATE TABLE narratives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id),
    topic TEXT, -- e.g., 'Saúde', 'Segurança'
    sentiment TEXT, -- 'positive', 'negative', 'neutral'
    key_themes TEXT[], -- Array de temas extraídos (pelo Worker)
    is_misinformation BOOLEAN DEFAULT false,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_posts_profile ON posts(profile_id);
CREATE INDEX idx_engagement_post ON engagement_history(post_id);
CREATE INDEX idx_narratives_post ON narratives(post_id);
