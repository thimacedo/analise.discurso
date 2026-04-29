# Sentinela Democrática — Agente de Extração de Dados do Instagram

> Sistema automatizado de monitoramento de discurso em perfis do Instagram, baseado em Scrapy com Playwright, armazenamento no Supabase e agendamento bi-diário.

---

## Sumário

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Estrutura de Diretórios](#2-estrutura-de-diretórios)
3. [Schema do Banco de Dados — Supabase](#3-schema-do-banco-de-dados--supabase)
4. [Variáveis de Ambiente](#4-variáveis-de-ambiente)
5. [Dependências](#5-dependências)
6. [Configuração do Scrapy](#6-configuração-do-scrapy)
7. [Definição dos Itens](#7-definição-dos-itens)
8. [Pipeline Supabase](#8-pipeline-supabase)
9. [Spider Principal do Instagram](#9-spider-principal-do-instagram)
10. [Deduplicação e Controle de Estado](#10-deduplicação-e-controle-de-estado)
11. [Agendamento Bi-diário](#11-agendamento-bi-diário)
12. [Middlewares e Anti-Detecção](#12-middlewares-e-anti-detecção)
13. [Utilitários Auxiliares](#13-utilitários-auxiliares)
14. [Docker e Deploy](#14-docker-e-deploy)
15. [Fluxo Completo de Execução](#15-fluxo-completo-de-execução)
16. [Notas e Advertências](#16-notas-e-advertências)

---

## 1. Visão Geral da Arquitetura

O sistema **Sentinela Democrática** opera em um ciclo contínuo de coleta, processamento e armazenamento de dados do Instagram. A arquitetura é composta por cinco camadas principais:

```
┌──────────────────────────────────────────────────────────────┐
│                    AGENDADOR (schedule)                       │
│                  2x/dia: 08:00 e 20:00                       │
└──────────────┬───────────────────────────────────────────────┘
               │ dispara
               ▼
┌──────────────────────────────────────────────────────────────┐
│              SCRAPY + PLAYWRIGHT (Spider)                     │
│                                                               │
│  1. Acessa instagram.com/monitoramento.discurso               │
│  2. Extrai lista de perfis seguidos                           │
│  3. Para cada perfil, coleta os 3 últimos posts               │
│  4. Para cada post, coleta até 100 comentários                │
│  5. Deduplicação via banco (upsert por ID)                    │
└──────────────┬───────────────────────────────────────────────┘
               │ itens yieldados
               ▼
┌──────────────────────────────────────────────────────────────┐
│              PIPELINE SUPABASE                                 │
│                                                               │
│  - InstagramProfileItem → tabela profiles (upsert)            │
│  - InstagramPostItem   → tabela posts   (upsert)              │
│  - InstagramCommentItem→ tabela comments (upsert)             │
└──────────────┬───────────────────────────────────────────────┘
               │ dados persistidos
               ▼
┌──────────────────────────────────────────────────────────────┐
│                   SUPABASE (PostgreSQL)                        │
│                                                               │
│  Tabelas: profiles, posts, comments, extraction_runs          │
│  Vistas: vw_unclassified_comments, vw_run_stats               │
└──────────────────────────────────────────────────────────────┘
```

### Estratégia de Coleta Híbrida

O spider utiliza uma **estratégia híbrida** que combina Playwright e requisições HTTP diretas:

1. **Playwright** é utilizado para o login e captura de cookies de sessão (necessário para autenticação no Instagram).
2. **Requisições HTTP diretas** são feitas aos endpoints GraphQL/REST do Instagram usando os cookies capturados, o que é significativamente mais rápido e leve que renderizar cada página no navegador.

Essa abordagem reduz o consumo de recursos e minimiza o risco de detecção, pois a navegação com Playwright é utilizada apenas no momento do login, enquanto a coleta de dados em si ocorre via chamadas API de alto desempenho.

---

## 2. Estrutura de Diretórios

```
sentinela_democratica/
├── scrapy.cfg                          # Configuração de deploy do Scrapy
├── requirements.txt                    # Dependências Python
├── .env                                # Variáveis de ambiente (NÃO versionar)
├── .env.example                        # Exemplo de variáveis de ambiente
├── main.py                             # Script de agendamento (ponto de entrada)
├── docker-compose.yml                  # Container para deploy
├── Dockerfile                          # Imagem do agente
├── instagram_bot/
│   ├── __init__.py
│   ├── settings.py                     # Configurações do Scrapy
│   ├── items.py                        # Definição dos itens (data models)
│   ├── pipelines.py                    # Pipeline de inserção no Supabase
│   ├── middlewares.py                  # Middlewares de anti-detecção
│   ├── utils.py                        # Funções utilitárias
│   └── spiders/
│       ├── __init__.py
│       └── instagram.py                # Spider principal
└── sql/
    └── schema.sql                      # Schema completo do Supabase
```

---

## 3. Schema do Banco de Dados — Supabase

O schema foi projetado para garantir integridade referencial, deduplicação automática via `upsert` e rastreabilidade completa de cada ciclo de extração.

### `sql/schema.sql`

```sql
-- ============================================================
-- SENTINELA DEMOCRÁTICA — Schema do Banco de Dados
-- Banco: Supabase (PostgreSQL 15+)
-- ============================================================

-- ----------------------------------------------------------
-- 1. Tabela de execuções (cada vez que o agente roda)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS extraction_runs (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'running'
                    CHECK (status IN ('running','success','partial','failed')),
    profiles_found  INTEGER DEFAULT 0,
    posts_found     INTEGER DEFAULT 0,
    comments_found  INTEGER DEFAULT 0,
    error_message   TEXT
);

-- ----------------------------------------------------------
-- 2. Tabela de perfis monitorados
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS profiles (
    user_id         TEXT PRIMARY KEY,            -- ID numérico do Instagram
    username        TEXT NOT NULL,               -- @username
    full_name       TEXT DEFAULT '',             -- Nome de exibição
    bio             TEXT DEFAULT '',             -- Biografia
    is_verified     BOOLEAN DEFAULT FALSE,       -- Selo de verificação
    followers_count INTEGER DEFAULT 0,           -- Número de seguidores
    following_count INTEGER DEFAULT 0,           -- Número de seguidos
    profile_pic_url TEXT DEFAULT '',             -- URL da foto de perfil
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_active       BOOLEAN DEFAULT TRUE         -- Se ainda é seguido pelo monitor
);

-- Índice para busca por username
CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles (username);

-- ----------------------------------------------------------
-- 3. Tabela de postagens
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS posts (
    post_id         TEXT PRIMARY KEY,            -- ID numérico do post no Instagram
    shortcode       TEXT NOT NULL,               -- Código curto (ex: Cxyz123)
    owner_username  TEXT NOT NULL,               -- Username do autor
    owner_id        TEXT DEFAULT '',             -- ID numérico do autor
    text            TEXT DEFAULT '',             -- Legenda/caption
    timestamp       TIMESTAMPTZ,                 -- Data/hora da publicação
    likes_count     INTEGER DEFAULT 0,
    comments_count  INTEGER DEFAULT 0,
    is_video        BOOLEAN DEFAULT FALSE,
    display_url     TEXT DEFAULT '',
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_posts_shortcode ON posts (shortcode);
CREATE INDEX IF NOT EXISTS idx_posts_owner     ON posts (owner_username);
CREATE INDEX IF NOT EXISTS idx_posts_timestamp ON posts (timestamp DESC);

-- ----------------------------------------------------------
-- 4. Tabela de comentários
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS comments (
    comment_id      TEXT PRIMARY KEY,            -- ID numérico do comentário
    post_shortcode  TEXT NOT NULL,               -- Shortcode do post pai
    owner_username  TEXT NOT NULL,               -- Username do comentarista
    owner_id        TEXT DEFAULT '',             -- ID numérico do comentarista
    text            TEXT NOT NULL,               -- Texto do comentário
    timestamp       TIMESTAMPTZ,                 -- Data/hora do comentário
    likes_count     INTEGER DEFAULT 0,
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Chave estrangeira para o post (comentário pertence a um post)
    FOREIGN KEY (post_shortcode) REFERENCES posts (shortcode) ON DELETE CASCADE
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_comments_post     ON comments (post_shortcode);
CREATE INDEX IF NOT EXISTS idx_comments_owner    ON comments (owner_username);
CREATE INDEX IF NOT EXISTS idx_comments_timestamp ON comments (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_comments_text     ON comments USING gin(to_tsvector('portuguese', text));

-- ----------------------------------------------------------
-- 5. View: comentários não classificados
--    (prontos para análise pelo módulo de classificação)
-- ----------------------------------------------------------
CREATE OR REPLACE VIEW vw_unclassified_comments AS
SELECT
    c.comment_id,
    c.post_shortcode,
    c.owner_username,
    c.text,
    c.timestamp,
    p.owner_username AS post_author,
    p.text           AS post_caption
FROM comments c
JOIN posts p ON p.shortcode = c.post_shortcode
ORDER BY c.timestamp DESC;

-- ----------------------------------------------------------
-- 6. View: estatísticas por execução
-- ----------------------------------------------------------
CREATE OR REPLACE VIEW vw_run_stats AS
SELECT
    id,
    started_at,
    finished_at,
    status,
    profiles_found,
    posts_found,
    comments_found,
    EXTRACT(EPOCH FROM (finished_at - started_at))::INTEGER AS duration_seconds
FROM extraction_runs
ORDER BY started_at DESC;

-- ----------------------------------------------------------
-- 7. Função: marcar perfis inativos
--    (perfis que não foram encontrados na última execução)
-- ----------------------------------------------------------
CREATE OR REPLACE FUNCTION mark_inactive_profiles()
RETURNS void AS $$
BEGIN
    UPDATE profiles
    SET is_active = FALSE
    WHERE user_id NOT IN (
        SELECT DISTINCT user_id
        FROM profiles
        WHERE last_checked_at > now() - INTERVAL '1 day'
    );
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------
-- 8. Row Level Security (RLS) — recomendado para Supabase
-- ----------------------------------------------------------
ALTER TABLE extraction_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles        ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts           ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments        ENABLE ROW LEVEL SECURITY;

-- Política: permitir tudo para o service_role (usado pelo agente)
CREATE POLICY "Service role full access" ON extraction_runs FOR ALL USING (true);
CREATE POLICY "Service role full access" ON profiles        FOR ALL USING (true);
CREATE POLICY "Service role full access" ON posts           FOR ALL USING (true);
CREATE POLICY "Service role full access" ON comments        FOR ALL USING (true);
```

---

## 4. Variáveis de Ambiente

### `.env.example`

```bash
# ============================================================
# SENTINELA DEMOCRÁTICA — Variáveis de Ambiente
# ============================================================

# --- Supabase ---
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx

# --- Instagram ---
IG_USERNAME=seu_usuario_aqui
IG_PASSWORD=sua_senha_aqui
IG_SESSION_ID=                          # Opcional: sessionid já válido (evita login)

# --- Agendamento ---
SCHEDULE_TIMES=08:00,20:00              # Horários de execução (separados por vírgula)

# --- Playwright ---
PLAYWRIGHT_HEADLESS=true                # true para produção, false para debug
PLAYWRIGHT_USER_DATA_DIR=/tmp/ig_session # Diretório de sessão persistente

# --- Scraping ---
DOWNLOAD_DELAY=3                        # Segundos entre requisições
CONCURRENT_REQUESTS=1                   # Requisições simultâneas (manter baixo)
MAX_COMMENTS_PER_POST=100              # Limite de comentários por post
MAX_POSTS_PER_PROFILE=3                # Limite de posts por perfil
```

---

## 5. Dependências

### `requirements.txt`

```text
Scrapy>=2.11.0
scrapy-playwright>=0.0.33
supabase>=2.3.0
schedule>=1.2.1
python-dotenv>=1.0.0
fake-useragent>=1.4.0
```

Instalação completa (incluindo o navegador Playwright):

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 6. Configuração do Scrapy

### `scrapy.cfg`

```ini
[settings]
default = instagram_bot.settings

[deploy]
project = instagram_bot
```

### `instagram_bot/settings.py`

```python
"""
Configurações do projeto Scrapy para o agente Sentinela Democrática.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "instagram_bot"

SPIDER_MODULES = ["instagram_bot.spiders"]
NEWSPIDER_MODULE = "instagram_bot.spiders"

# Não respeitar robots.txt (necessário para endpoints de API)
ROBOTSTXT_OBEY = False

# ---------------------------------------------------------------
# Reactor asyncio (OBRIGATÓRIO para scrapy-playwright)
# ---------------------------------------------------------------
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# ---------------------------------------------------------------
# Download handlers — Playwright para HTTP/HTTPS
# ---------------------------------------------------------------
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# ---------------------------------------------------------------
# Configuração do Playwright
# ---------------------------------------------------------------
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true",
    "timeout": 60_000,
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-web-security",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ],
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60_000

# Contexto persistente para manter a sessão logada entre execuções
PLAYWRIGHT_CONTEXTS = {
    "logged_in": {
        "user_data_dir": os.getenv("PLAYWRIGHT_USER_DATA_DIR", "/tmp/ig_session"),
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "locale": "pt-BR",
        "timezone_id": "America/Fortaleza",
    },
}

# Abortar recursos desnecessários (imagens, CSS, fontes) para acelerar
def should_abort_request(request):
    """Filtra recursos que não são necessários para a coleta de dados."""
    return request.resource_type in ("image", "stylesheet", "font", "media")

PLAYWRIGHT_ABORT_REQUEST = should_abort_request

# ---------------------------------------------------------------
# Rate limiting — ser respeitoso para evitar bloqueios
# ---------------------------------------------------------------
DOWNLOAD_DELAY = int(os.getenv("DOWNLOAD_DELAY", "3"))
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "1"))

# ---------------------------------------------------------------
# Headers padrão simulando navegador real
# ---------------------------------------------------------------
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
}

# ---------------------------------------------------------------
# Pipelines — inserção no Supabase
# ---------------------------------------------------------------
ITEM_PIPELINES = {
    "instagram_bot.pipelines.SupabasePipeline": 300,
}

# ---------------------------------------------------------------
# Middlewares de anti-detecção
# ---------------------------------------------------------------
DOWNLOADER_MIDDLEWARES = {
    "instagram_bot.middlewares.AntiDetectionMiddleware": 400,
}

# ---------------------------------------------------------------
# Configurações gerais
# ---------------------------------------------------------------
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

# Timeout
DOWNLOAD_TIMEOUT = 30

# AutoThrottle (ajuste automático de velocidade)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 15
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
```

---

## 7. Definição dos Itens

### `instagram_bot/items.py`

```python
"""
Definição das estruturas de dados (Itens) coletados pelo Scrapy.

Cada item corresponde a uma entidade no banco de dados Supabase:
- InstagramProfileItem  → tabela profiles
- InstagramPostItem    → tabela posts
- InstagramCommentItem → tabela comments
"""

import scrapy


class InstagramProfileItem(scrapy.Item):
    """Item representando um perfil monitorado no Instagram."""

    type = scrapy.Field()             # "profile"
    user_id = scrapy.Field()          # ID numérico do Instagram
    username = scrapy.Field()         # @username
    full_name = scrapy.Field()        # Nome de exibição
    bio = scrapy.Field()              # Biografia do perfil
    is_verified = scrapy.Field()      # Selo de verificação
    followers_count = scrapy.Field()  # Número de seguidores
    following_count = scrapy.Field()  # Número de seguidos
    profile_pic_url = scrapy.Field()  # URL da foto de perfil


class InstagramPostItem(scrapy.Item):
    """Item representando uma postagem de um perfil monitorado."""

    type = scrapy.Field()             # "post"
    post_id = scrapy.Field()          # ID numérico do post
    shortcode = scrapy.Field()        # Código curto (ex: Cxyz123)
    owner_username = scrapy.Field()   # Username do autor
    owner_id = scrapy.Field()         # ID numérico do autor
    text = scrapy.Field()             # Legenda/caption
    timestamp = scrapy.Field()        # Data/hora de publicação (epoch)
    likes_count = scrapy.Field()      # Número de curtidas
    comments_count = scrapy.Field()   # Número de comentários
    is_video = scrapy.Field()         # Se é um vídeo
    display_url = scrapy.Field()      # URL da imagem de exibição


class InstagramCommentItem(scrapy.Item):
    """Item representando um comentário em uma postagem."""

    type = scrapy.Field()             # "comment"
    comment_id = scrapy.Field()       # ID numérico do comentário
    post_shortcode = scrapy.Field()   # Shortcode do post pai
    owner_username = scrapy.Field()   # Username do comentarista
    owner_id = scrapy.Field()         # ID numérico do comentarista
    text = scrapy.Field()             # Texto do comentário
    timestamp = scrapy.Field()        # Data/hora do comentário (epoch)
    likes_count = scrapy.Field()      # Número de curtidas no comentário


class ExtractionRunItem(scrapy.Item):
    """Item para registrar o início e fim de uma execução."""

    type = scrapy.Field()             # "run_start" ou "run_end"
    run_id = scrapy.Field()           # UUID da execução
    status = scrapy.Field()           # running, success, partial, failed
    profiles_found = scrapy.Field()   # Contagem de perfis encontrados
    posts_found = scrapy.Field()      # Contagem de posts encontrados
    comments_found = scrapy.Field()   # Contagem de comentários encontrados
    error_message = scrapy.Field()    # Mensagem de erro, se houver
```

---

## 8. Pipeline Supabase

### `instagram_bot/pipelines.py`

```python
"""
Pipeline para processamento e armazenamento dos itens no Supabase.

Utiliza upsert para garantir idempotência — itens duplicados são
atualizados em vez de causar erros de chave primária duplicada.
"""

import os
import logging
import datetime
from supabase import create_client, Client

from instagram_bot.items import (
    InstagramProfileItem,
    InstagramPostItem,
    InstagramCommentItem,
    ExtractionRunItem,
)

logger = logging.getLogger(__name__)


class SupabasePipeline:
    """
    Pipeline responsável por conectar ao banco de dados Supabase e
    inserir/atualizar os registros coletados pelo spider.

    A estratégia de upsert garante que:
    - Registros novos são inseridos normalmente
    - Registros já existentes (mesma PK) são atualizados com os dados mais recentes
    - Não há erros de duplicação ao rodar o agente múltiplas vezes
    """

    def __init__(self):
        """Inicializa a conexão com o Supabase usando variáveis de ambiente."""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são obrigatórias. "
                "Configure-as no arquivo .env ou no ambiente de execução."
            )

        self.supabase: Client = create_client(url, key)
        self.run_id = None
        self.stats = {"profiles": 0, "posts": 0, "comments": 0}

    def open_spider(self, spider):
        """
        Chamado quando o spider é iniciado. Registra o início da execução
        na tabela extraction_runs.
        """
        try:
            result = (
                self.supabase.table("extraction_runs")
                .insert({
                    "status": "running",
                    "profiles_found": 0,
                    "posts_found": 0,
                    "comments_found": 0,
                })
                .execute()
            )
            self.run_id = result.data[0]["id"]
            spider.logger.info(f"Execução registrada com ID: {self.run_id}")
        except Exception as e:
            spider.logger.error(f"Erro ao registrar execução: {e}")

    def close_spider(self, spider):
        """
        Chamado quando o spider termina. Atualiza o registro da execução
        com as contagens finais e o status de conclusão.
        """
        try:
            if self.run_id:
                self.supabase.table("extraction_runs").update({
                    "finished_at": datetime.datetime.now(
                        tz=datetime.timezone.utc
                    ).isoformat(),
                    "status": "success",
                    "profiles_found": self.stats["profiles"],
                    "posts_found": self.stats["posts"],
                    "comments_found": self.stats["comments"],
                }).eq("id", self.run_id).execute()

                spider.logger.info(
                    f"Execução finalizada: {self.stats['profiles']} perfis, "
                    f"{self.stats['posts']} posts, {self.stats['comments']} comentários"
                )
        except Exception as e:
            spider.logger.error(f"Erro ao finalizar execução: {e}")

    def process_item(self, item, spider):
        """
        Identifica o tipo de item e o envia para a tabela correspondente
        no Supabase usando upsert (inserir ou atualizar).

        Args:
            item: O item extraído pelo spider.
            spider: A instância do spider em execução.

        Returns:
            O item processado (inalterado, para seguir o padrão Scrapy).
        """
        try:
            if isinstance(item, InstagramProfileItem):
                self._upsert_profile(item)
                self.stats["profiles"] += 1

            elif isinstance(item, InstagramPostItem):
                self._upsert_post(item)
                self.stats["posts"] += 1

            elif isinstance(item, InstagramCommentItem):
                self._upsert_comment(item)
                self.stats["comments"] += 1

            elif isinstance(item, ExtractionRunItem):
                self._handle_run_item(item)

        except Exception as e:
            spider.logger.error(
                f"Erro ao inserir item no Supabase: {e} | Item: {dict(item)}"
            )

        return item

    def _upsert_profile(self, item):
        """Insere ou atualiza um perfil na tabela profiles."""
        from datetime import datetime, timezone

        data = {
            "user_id": item.get("user_id"),
            "username": item.get("username"),
            "full_name": item.get("full_name", ""),
            "bio": item.get("bio", ""),
            "is_verified": item.get("is_verified", False),
            "followers_count": item.get("followers_count", 0),
            "following_count": item.get("following_count", 0),
            "profile_pic_url": item.get("profile_pic_url", ""),
            "last_checked_at": datetime.now(tz=timezone.utc).isoformat(),
            "is_active": True,
        }
        self.supabase.table("profiles").upsert(data, on_conflict="user_id").execute()

    def _upsert_post(self, item):
        """Insere ou atualiza uma postagem na tabela posts."""
        from datetime import datetime, timezone

        timestamp = item.get("timestamp")
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

        data = {
            "post_id": item.get("post_id"),
            "shortcode": item.get("shortcode"),
            "owner_username": item.get("owner_username"),
            "owner_id": item.get("owner_id", ""),
            "text": item.get("text", ""),
            "timestamp": timestamp,
            "likes_count": item.get("likes_count", 0),
            "comments_count": item.get("comments_count", 0),
            "is_video": item.get("is_video", False),
            "display_url": item.get("display_url", ""),
            "last_seen_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self.supabase.table("posts").upsert(data, on_conflict="post_id").execute()

    def _upsert_comment(self, item):
        """Insere ou atualiza um comentário na tabela comments."""
        from datetime import datetime, timezone

        timestamp = item.get("timestamp")
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

        data = {
            "comment_id": item.get("comment_id"),
            "post_shortcode": item.get("post_shortcode"),
            "owner_username": item.get("owner_username"),
            "owner_id": item.get("owner_id", ""),
            "text": item.get("text", ""),
            "timestamp": timestamp,
            "likes_count": item.get("likes_count", 0),
            "last_seen_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self.supabase.table("comments").upsert(
            data, on_conflict="comment_id"
        ).execute()

    def _handle_run_item(self, item):
        """Trata itens de controle de execução."""
        if item.get("type") == "run_end" and self.run_id:
            self.supabase.table("extraction_runs").update({
                "status": item.get("status", "success"),
                "error_message": item.get("error_message"),
            }).eq("id", self.run_id).execute()
```

---

## 9. Spider Principal do Instagram

### `instagram_bot/spiders/instagram.py`

```python
"""
Spider principal do Sentinela Democrática para extração de dados do Instagram.

Estratégia híbrida:
1. Login via Playwright (renderização de navegador para autenticação)
2. Interceptação de cookies/CSRF token da sessão autenticada
3. Requisições HTTP diretas aos endpoints GraphQL/REST do Instagram
   usando os cookies capturados — muito mais rápido que Playwright por página

Fluxo de coleta:
  Perfil monitor → Perfis seguidos → 3 últimos posts de cada → Até 100 comentários por post
"""

import os
import json
import asyncio
import scrapy
from datetime import datetime, timezone
from playwright.async_api import Page, Response as PlaywrightResponse

from instagram_bot.items import (
    InstagramProfileItem,
    InstagramPostItem,
    InstagramCommentItem,
)


class InstagramSpider(scrapy.Spider):
    """
    Spider do Scrapy para extrair perfis seguidos pelo perfil monitor,
    suas postagens recentes e comentários.

    O spider opera em duas fases:
    - Fase 1 (Login): Usa Playwright para autenticar no Instagram
      e capturar os cookies de sessão.
    - Fase 2 (Coleta): Faz requisições HTTP diretas aos endpoints
      da API do Instagram usando os cookies capturados.
    """

    name = "instagram"
    allowed_domains = ["instagram.com", "i.instagram.com"]

    # ---------------------------------------------------------------
    # Configurações do perfil monitor
    # ---------------------------------------------------------------
    MONITOR_USERNAME = "monitoramento.discurso"

    # Credenciais (lidas do ambiente)
    IG_USERNAME = os.getenv("IG_USERNAME", "")
    IG_PASSWORD = os.getenv("IG_PASSWORD", "")
    IG_SESSION_ID = os.getenv("IG_SESSION_ID", "")

    # Limites configuráveis
    MAX_POSTS_PER_PROFILE = int(os.getenv("MAX_POSTS_PER_PROFILE", "3"))
    MAX_COMMENTS_PER_POST = int(os.getenv("MAX_COMMENTS_PER_POST", "100"))

    # App ID público do Instagram Web (necessário em todas as requisições)
    X_IG_APP_ID = "936619743392459"

    # Sessão capturada do Playwright
    _session_cookies = {}
    _csrf_token = ""

    # Doc IDs do GraphQL (podem mudar periodicamente — atualizar via DevTools)
    # Estes são os identificadores de consulta que o Instagram usa internamente.
    # Se pararem de funcionar, abra o DevTools do navegador, vá na aba Network,
    # filtre por "graphql" e copie os doc_id atuais das requisições.
    DOC_ID_FOLLOWING = "d04b0a864b4b54837c0d870b0e77e076"
    DOC_ID_USER_POSTS = "8c2a529969ee035a5063f2fc8602a0fd"
    DOC_ID_COMMENTS = "bc3296d1ce80c24cbda7840ec8c0d10f"

    custom_settings = {
        "PLAYWRIGHT_MAX_CONTEXTS": 1,
    }

    # ===============================================================
    # FASE 1: Login via Playwright
    # ===============================================================

    def start_requests(self):
        """
        Ponto de entrada do spider. Tenta primeiro usar um sessionid
        já válido (se fornecido via ambiente). Caso contrário, faz
        login via Playwright.
        """
        if self.IG_SESSION_ID:
            self.logger.info("Usando sessionid fornecido via variável de ambiente")
            self._session_cookies = {"sessionid": self.IG_SESSION_ID}
            # Buscar o CSRF token junto com o sessionid
            # (normalmente o cookie csrftoken já vem com a sessão)
            yield scrapy.Request(
                url=f"https://www.instagram.com/{self.MONITOR_USERNAME}/",
                headers=self._build_api_headers(),
                meta={"playwright": False},
                callback=self._fetch_monitor_profile_via_api,
                dont_filter=True,
            )
        else:
            self.logger.info("Iniciando login via Playwright...")
            yield scrapy.Request(
                url="https://www.instagram.com/accounts/login/",
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context": "logged_in",
                    "playwright_page_goto_kwargs": {"wait_until": "networkidle"},
                },
                callback=self._login,
                errback=self._errback_close_page,
                dont_filter=True,
            )

    async def _login(self, response):
        """
        Realiza o login no Instagram via Playwright e captura os cookies
        de sessão para uso nas requisições HTTP subsequentes.
        """
        page: Page = response.meta["playwright_page"]

        try:
            # Aguardar o formulário de login carregar
            await page.wait_for_selector("input[name='username']", timeout=15_000)

            # Preencher credenciais
            await page.fill("input[name='username']", self.IG_USERNAME)
            await page.fill("input[name='password']", self.IG_PASSWORD)

            # Pequena pausa para simular comportamento humano
            await asyncio.sleep(1)

            # Clicar no botão de login
            await page.click("button[type='submit']")

            # Aguardar a navegação completar após o login
            await page.wait_for_load_state("networkidle", timeout=30_000)
            await asyncio.sleep(3)

            # Verificar se há popup de "Salvar informações de login"
            try:
                save_info_btn = page.locator("button", has_text="Agora não")
                if await save_info_btn.count() > 0:
                    await save_info_btn.first.click()
                    await asyncio.sleep(1)
            except Exception:
                pass

            # Verificar se há popup de notificações
            try:
                not_now_btn = page.locator("button", has_text="Agora não")
                if await not_now_btn.count() > 0:
                    await not_now_btn.first.click()
                    await asyncio.sleep(1)
            except Exception:
                pass

            # Capturar cookies da sessão autenticada
            cookies = await page.context.cookies()
            self._session_cookies = {
                c["name"]: c["value"]
                for c in cookies
                if c["name"] in ("sessionid", "csrftoken", "ds_user_id", "ig_did")
            }
            self._csrf_token = self._session_cookies.get("csrftoken", "")

            if "sessionid" not in self._session_cookies:
                self.logger.error(
                    "Login falhou: cookie 'sessionid' não encontrado. "
                    "Verifique as credenciais."
                )
                await page.close()
                return

            self.logger.info("Login realizado com sucesso! Cookies capturados.")

            # Fechar a página — não precisamos mais do navegador
            await page.close()

            # Iniciar a coleta via API HTTP
            yield scrapy.Request(
                url=f"https://www.instagram.com/{self.MONITOR_USERNAME}/",
                headers=self._build_api_headers(),
                meta={"playwright": False},
                callback=self._fetch_monitor_profile_via_api,
                dont_filter=True,
            )

        except Exception as e:
            self.logger.error(f"Erro durante o login: {e}")
            await page.close()

    # ===============================================================
    # FASE 2: Coleta via API HTTP (usando cookies da sessão)
    # ===============================================================

    def _build_api_headers(self):
        """
        Constrói os headers necessários para as requisições à API do Instagram.

        O header X-IG-App-ID é obrigatório e deve conter o ID público
        do aplicativo web do Instagram. Sem ele, todas as requisições
        retornam 403 Forbidden.
        """
        headers = {
            "X-IG-App-ID": self.X_IG_APP_ID,
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
            "Referer": "https://www.instagram.com/",
        }

        # Adicionar cookies como header
        cookie_str = "; ".join(
            f"{k}={v}" for k, v in self._session_cookies.items()
        )
        headers["Cookie"] = cookie_str

        # CSRF Token (necessário para requisições GraphQL POST)
        if self._csrf_token:
            headers["X-CSRFToken"] = self._csrf_token

        return headers

    def _fetch_monitor_profile_via_api(self, response):
        """
        Busca os dados do perfil monitor via API REST do Instagram
        para obter o user_id numérico necessário para consultar os seguidos.
        """
        url = (
            f"https://i.instagram.com/api/v1/users/web_profile_info/"
            f"?username={self.MONITOR_USERNAME}"
        )
        yield scrapy.Request(
            url,
            headers=self._build_api_headers(),
            callback=self._parse_monitor_profile,
            dont_filter=True,
        )

    def _parse_monitor_profile(self, response):
        """
        Processa a resposta do perfil monitor para obter o ID numérico
        e iniciar a paginação dos perfis seguidos.

        O Instagram requer o ID numérico (não o username) para consultar
        a lista de seguidos. Este ID é obtido através do endpoint
        web_profile_info.
        """
        try:
            data = json.loads(response.text)
            user = data.get("data", {}).get("user")

            if not user:
                self.logger.error(
                    f"Não foi possível obter dados do perfil monitor "
                    f"'{self.MONITOR_USERNAME}'. Resposta: {response.text[:500]}"
                )
                return

            user_id = user["id"]
            self.logger.info(
                f"Perfil monitor: {self.MONITOR_USERNAME} (ID: {user_id})"
            )

            # Iniciar a busca pelos perfis seguidos
            yield self._make_following_request(user_id, first=50, after_cursor=None)

        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(
                f"Erro ao analisar perfil monitor: {e} | "
                f"Status: {response.status} | Body: {response.text[:300]}"
            )

    # ---------------------------------------------------------------
    # Coleta de perfis seguidos
    # ---------------------------------------------------------------

    def _make_following_request(self, user_id, first=50, after_cursor=None):
        """
        Constrói e retorna uma requisição GraphQL para buscar a lista
        de perfis seguidos pelo perfil monitor.

        A paginação é baseada em cursor: cada resposta inclui um
        end_cursor para a próxima página, se houver.
        """
        variables = {"id": user_id, "first": first}
        if after_cursor:
            variables["after"] = after_cursor

        url = (
            f"https://www.instagram.com/graphql/query/"
            f"?query_hash={self.DOC_ID_FOLLOWING}"
            f"&variables={json.dumps(variables, separators=(',', ':'))}"
        )

        return scrapy.Request(
            url,
            headers=self._build_api_headers(),
            callback=self._parse_followings,
            cb_kwargs={"monitor_user_id": user_id},
            dont_filter=True,
        )

    def _parse_followings(self, response, monitor_user_id):
        """
        Processa a lista de perfis seguidos pelo perfil monitor.

        Para cada perfil seguido:
        1. Cria um InstagramProfileItem e o yielda para o pipeline
        2. Dispara uma requisição para coletar os posts desse perfil

        Se houver mais páginas (paginação por cursor), faz uma nova
        requisição para a próxima página.
        """
        try:
            data = json.loads(response.text)
            user_data = data.get("data", {}).get("user", {})

            if not user_data:
                self.logger.warning("Resposta sem dados de usuário em _parse_followings")
                return

            edge_follow = user_data.get("edge_follow", {})
            edges = edge_follow.get("edges", [])

            self.logger.info(f"Encontrados {len(edges)} perfis seguidos nesta página")

            for edge in edges:
                node = edge.get("node", {})
                if not node:
                    continue

                followed_id = node.get("id")
                followed_username = node.get("username")

                # Yield do item de perfil
                profile_item = InstagramProfileItem(
                    type="profile",
                    user_id=followed_id,
                    username=followed_username,
                    full_name=node.get("full_name", ""),
                    bio=node.get("biography", ""),
                    is_verified=node.get("is_verified", False),
                    followers_count=node.get("edge_followed_by", {}).get("count", 0),
                    following_count=node.get("edge_follow", {}).get("count", 0),
                    profile_pic_url=node.get("profile_pic_url_hd", ""),
                )
                yield profile_item

                # Requisição para os posts deste perfil
                yield self._make_user_posts_request(
                    user_id=followed_id,
                    username=followed_username,
                    first=self.MAX_POSTS_PER_PROFILE,
                )

            # Paginação: verificar se há mais páginas
            page_info = edge_follow.get("page_info", {})
            if page_info.get("has_next_page"):
                cursor = page_info.get("end_cursor")
                self.logger.info(f"Paginando seguidos com cursor: {cursor[:30]}...")
                yield self._make_following_request(
                    user_id=monitor_user_id,
                    first=50,
                    after_cursor=cursor,
                )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.error(
                f"Erro ao extrair seguidos: {e} | "
                f"Status: {response.status} | Body: {response.text[:300]}"
            )

    # ---------------------------------------------------------------
    # Coleta de postagens
    # ---------------------------------------------------------------

    def _make_user_posts_request(self, user_id, username, first=3, after_cursor=None):
        """
        Constrói e retorna uma requisição GraphQL para buscar as
        postagens recentes de um perfil.
        """
        variables = {"id": user_id, "first": first}
        if after_cursor:
            variables["after"] = after_cursor

        url = (
            f"https://www.instagram.com/graphql/query/"
            f"?query_hash={self.DOC_ID_USER_POSTS}"
            f"&variables={json.dumps(variables, separators=(',', ':'))}"
        )

        return scrapy.Request(
            url,
            headers=self._build_api_headers(),
            callback=self._parse_posts,
            cb_kwargs={"username": username, "user_id": user_id},
            dont_filter=True,
        )

    def _parse_posts(self, response, username, user_id):
        """
        Processa as postagens de um perfil seguido.

        Coleta apenas os N primeiros posts (conforme MAX_POSTS_PER_PROFILE).
        Para cada post, yielda um InstagramPostItem e dispara a coleta
        de comentários.
        """
        try:
            data = json.loads(response.text)
            user_data = data.get("data", {}).get("user", {})

            if not user_data:
                self.logger.warning(
                    f"Sem dados de usuário para posts de {username}"
                )
                return

            timeline = user_data.get("edge_owner_to_timeline_media", {})
            edges = timeline.get("edges", [])

            # Filtrar apenas posts (não reels/stories que podem aparecer)
            post_edges = [e for e in edges if e.get("node", {}).get("__typename") in (
                "GraphImage", "GraphSidecar", "GraphVideo"
            )]

            # Limitar ao número configurado de posts
            limited_edges = post_edges[: self.MAX_POSTS_PER_PROFILE]

            self.logger.info(
                f"Encontrados {len(limited_edges)} posts para @{username}"
            )

            for edge in limited_edges:
                node = edge.get("node", {})
                if not node:
                    continue

                shortcode = node.get("shortcode")

                # Extrair caption/texto do post
                text = ""
                caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                if caption_edges:
                    text = caption_edges[0].get("node", {}).get("text", "")

                # Yield do item de post
                post_item = InstagramPostItem(
                    type="post",
                    post_id=node.get("id"),
                    shortcode=shortcode,
                    owner_username=username,
                    owner_id=user_id,
                    text=text,
                    timestamp=node.get("taken_at_timestamp"),
                    likes_count=node.get("edge_media_preview_like", {}).get("count", 0),
                    comments_count=node.get("edge_media_to_comment", {}).get("count", 0),
                    is_video=node.get("is_video", False),
                    display_url=node.get("display_url", ""),
                )
                yield post_item

                # Iniciar coleta de comentários para este post
                yield self._make_comments_request(
                    shortcode=shortcode,
                    first=50,
                    after_cursor=None,
                    collected_count=0,
                )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.error(
                f"Erro ao extrair postagens para @{username}: {e} | "
                f"Body: {response.text[:300]}"
            )

    # ---------------------------------------------------------------
    # Coleta de comentários
    # ---------------------------------------------------------------

    def _make_comments_request(
        self, shortcode, first=50, after_cursor=None, collected_count=0
    ):
        """
        Constrói e retorna uma requisição GraphQL para buscar os
        comentários de uma postagem.

        O parâmetro collected_count rastreia quantos comentários já
        foram coletados para garantir que não ultrapasse o limite
        de MAX_COMMENTS_PER_POST.
        """
        if collected_count >= self.MAX_COMMENTS_PER_POST:
            return None

        variables = {"shortcode": shortcode, "first": first}
        if after_cursor:
            variables["after"] = after_cursor

        url = (
            f"https://www.instagram.com/graphql/query/"
            f"?query_hash={self.DOC_ID_COMMENTS}"
            f"&variables={json.dumps(variables, separators=(',', ':'))}"
        )

        return scrapy.Request(
            url,
            headers=self._build_api_headers(),
            callback=self._parse_comments,
            cb_kwargs={
                "shortcode": shortcode,
                "collected_count": collected_count,
            },
            dont_filter=True,
        )

    def _parse_comments(self, response, shortcode, collected_count):
        """
        Processa os comentários de uma postagem.

        Para cada comentário:
        1. Cria um InstagramCommentItem com os dados do comentário
        2. Incrementa o contador de comentários coletados

        Se o limite de MAX_COMMENTS_PER_POST ainda não foi atingido
        e há mais páginas de comentários, faz uma nova requisição.
        """
        try:
            data = json.loads(response.text)
            media = data.get("data", {}).get("shortcode_media")

            if not media:
                self.logger.debug(
                    f"Sem dados de mídia para comentários do post {shortcode}"
                )
                return

            edge_comments = media.get("edge_media_to_parent_comment", {})
            if not edge_comments:
                # Alguns posts usam um campo diferente
                edge_comments = media.get("edge_media_to_comment", {})

            edges = edge_comments.get("edges", [])

            for edge in edges:
                # Verificar o limite antes de processar cada comentário
                if collected_count >= self.MAX_COMMENTS_PER_POST:
                    self.logger.info(
                        f"Limite de {self.MAX_COMMENTS_PER_POST} comentários "
                        f"atingido para o post {shortcode}"
                    )
                    break

                node = edge.get("node", {})
                if not node:
                    continue

                owner = node.get("owner", {})

                comment_item = InstagramCommentItem(
                    type="comment",
                    comment_id=node.get("id"),
                    post_shortcode=shortcode,
                    owner_username=owner.get("username", ""),
                    owner_id=owner.get("id", ""),
                    text=node.get("text", ""),
                    timestamp=node.get("created_at"),
                    likes_count=node.get("edge_liked_by", {}).get("count", 0),
                )
                yield comment_item
                collected_count += 1

                # Processar respostas (comentários filhos) se existirem
                thread = node.get("edge_threaded_comments", {})
                thread_edges = thread.get("edges", [])
                for thread_edge in thread_edges:
                    if collected_count >= self.MAX_COMMENTS_PER_POST:
                        break
                    thread_node = thread_edge.get("node", {})
                    if not thread_node:
                        continue
                    thread_owner = thread_node.get("owner", {})
                    reply_item = InstagramCommentItem(
                        type="comment",
                        comment_id=thread_node.get("id"),
                        post_shortcode=shortcode,
                        owner_username=thread_owner.get("username", ""),
                        owner_id=thread_owner.get("id", ""),
                        text=thread_node.get("text", ""),
                        timestamp=thread_node.get("created_at"),
                        likes_count=thread_node.get("edge_liked_by", {}).get("count", 0),
                    )
                    yield reply_item
                    collected_count += 1

            # Paginação: verificar se há mais comentários
            page_info = edge_comments.get("page_info", {})
            if page_info.get("has_next_page") and collected_count < self.MAX_COMMENTS_PER_POST:
                cursor = page_info.get("end_cursor")
                next_request = self._make_comments_request(
                    shortcode=shortcode,
                    first=50,
                    after_cursor=cursor,
                    collected_count=collected_count,
                )
                if next_request:
                    yield next_request

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.error(
                f"Erro ao extrair comentários do post {shortcode}: {e} | "
                f"Body: {response.text[:300]}"
            )

    # ===============================================================
    # Utilitários
    # ===============================================================

    async def _errback_close_page(self, failure):
        """
        Callback de erro que fecha a página do Playwright para evitar
        vazamento de recursos. Toda requisição com playwright_include_page=True
        deve ter este errback configurado.
        """
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(
            f"Erro na requisição Playwright: {failure.request.url} | {failure.value}"
        )
```

---

## 10. Deduplicação e Controle de Estado

A deduplicação é garantida em **três camadas** complementares que trabalham em conjunto para assegurar que nenhum dado seja duplicado no banco de dados, mesmo quando o agente é executado múltiplas vezes sobre os mesmos perfis e postagens.

### Camada 1: Upsert no Supabase (Pipeline)

A estratégia principal de deduplicação é o uso de `upsert` (INSERT ON CONFLICT UPDATE) no pipeline do Supabase. Cada tabela possui uma chave primária natural que identifica unicamente o registro:

| Tabela | Chave Primária | Lógica de Upsert |
|--------|---------------|------------------|
| `profiles` | `user_id` | Se o perfil já existe, atualiza `last_checked_at` e dados de contagem |
| `posts` | `post_id` | Se o post já existe, atualiza `last_seen_at` e contagens de likes/comentários |
| `comments` | `comment_id` | Se o comentário já existe, atualiza `last_seen_at` e contagem de likes |

Isso significa que comentários já coletados em execuções anteriores serão simplesmente atualizados com os dados mais recentes, sem criar duplicatas.

### Camada 2: Controle de Posts por Perfil

O spider limita estritamente a coleta aos `MAX_POSTS_PER_PROFILE` (padrão: 3) posts mais recentes de cada perfil. Como o Instagram retorna os posts em ordem cronológica reversa, os 3 primeiros são sempre os mais recentes. Mesmo que um post anterior já tenha sido coletado, o `upsert` garante que ele será atualizado e não duplicado.

### Camada 3: Contagem de Comentários

O parâmetro `collected_count` é passado recursivamente entre as chamadas de paginação de comentários. Quando `collected_count` atinge `MAX_COMMENTS_PER_POST` (padrão: 100), a paginação é interrompida imediatamente, evitando a coleta desnecessária de comentários adicionais.

---

## 11. Agendamento Bi-diário

### `main.py`

```python
"""
Script de agendamento responsável por executar o crawler do Scrapy
duas vezes ao dia.

Este script é o ponto de entrada principal do agente Sentinela Democrática.
Ele carrega as variáveis de ambiente, configura os horários de execução
e mantém o processo rodando em loop para verificar o agendamento.

Uso:
    python main.py

Variáveis de ambiente relevantes:
    SCHEDULE_TIMES  — Horários de execução separados por vírgula (padrão: "08:00,20:00")
"""

import os
import sys
import time
import signal
import logging
import traceback
from datetime import datetime

import schedule
from dotenv import load_dotenv

# Garantir que o diretório do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_loadenv = load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("sentinela_scheduler")


def run_spider():
    """
    Inicializa e executa o processo do Scrapy com as configurações do projeto.

    Utiliza CrawlerProcess para executar o spider de forma isolada.
    Cada execução cria um novo processo, garantindo que não haja
    estado residual entre execuções.

    Após a conclusão (ou erro), registra o resultado no log e, em caso
    de falha, grava os detalhes do erro em um arquivo de log local.
    """
    try:
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        from instagram_bot.spiders.instagram import InstagramSpider

        logger.info("=" * 60)
        logger.info("Iniciando execução do Spider Sentinela Democrática")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)

        settings = get_project_settings()
        process = CrawlerProcess(settings)
        process.crawl(InstagramSpider)
        process.start()  # Bloqueia até o spider terminar

        logger.info("Execução do Spider concluída com sucesso")

    except Exception as e:
        logger.error(f"Erro na execução do Spider: {e}")
        _log_error(f"Erro na execução agendada do Spider: {e}\n{traceback.format_exc()}")


def _log_error(message):
    """
    Registra erros em um arquivo de log local para diagnóstico.

    O arquivo é salvo em /tmp/sentinela_scheduler_error.log para
    compatibilidade com ambientes Linux/Docker.
    """
    log_path = "/tmp/sentinela_scheduler_error.log"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def main():
    """
    Ponto de entrada principal que configura o agendamento de execução.

    Lê os horários de execução da variável de ambiente SCHEDULE_TIMES
    (formato: "HH:MM,HH:MM") e configura o scheduler.

    O loop principal verifica o agendamento a cada 60 segundos.
    Um handler de sinal SIGINT/SIGTERM permite encerramento limpo.
    """
    # Configurar horários de execução
    schedule_times = os.getenv("SCHEDULE_TIMES", "08:00,20:00").split(",")
    schedule_times = [t.strip() for t in schedule_times if t.strip()]

    for scheduled_time in schedule_times:
        schedule.every().day.at(scheduled_time).do(run_spider)
        logger.info(f"Execução agendada para: {scheduled_time}")

    logger.info(
        f"Sentinela Democrática iniciado. Execuções agendadas: {schedule_times}"
    )

    # Handler para encerramento limpo
    running = True

    def signal_handler(signum, frame):
        nonlocal running
        logger.info("Sinal de encerramento recebido. Finalizando...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Loop principal
    while running:
        schedule.run_pending()
        time.sleep(60)

    logger.info("Sentinela Democrática encerrado.")


if __name__ == "__main__":
    main()
```

---

## 12. Middlewares e Anti-Detecção

### `instagram_bot/middlewares.py`

```python
"""
Middlewares do Scrapy para evitar detecção e bloqueio pelo Instagram.

O Instagram possui sistemas sofisticados de anti-scraping que incluem:
- Detecção de User-Agent padrão do Scrapy
- Rate limiting por IP
- Detecção de padrões de navegação automatizada
- Verificação de headers e fingerprints do navegador

Estes middlewares ajudam a simular o comportamento de um navegador real.
"""

import random
import logging

logger = logging.getLogger(__name__)


class AntiDetectionMiddleware:
    """
    Middleware de anti-detecção que modifica as requisições para
    simular o comportamento de um navegador real.

    Funcionalidades:
    - Rotação de User-Agent
    - Adição de headers realistas
    - jitter aleatório no timing de requisições
    """

    # Lista de User-Agens reais de navegadores Chrome em diferentes plataformas
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    ]

    def process_request(self, request, spider):
        """
        Processa cada requisição antes de enviá-la, adicionando
        headers de anti-detecção.

        Não modifica requisições que já usam Playwright (meta.playwright=True),
        pois o Playwright já gerencia os headers do navegador.
        """
        # Pular requisições que usam Playwright
        if request.meta.get("playwright"):
            return None

        # Rotacionar User-Agent
        request.headers["User-Agent"] = random.choice(self.USER_AGENTS)

        # Adicionar headers realistas que o Instagram espera
        if "instagram.com" in request.url:
            if "Sec-Ch-Ua" not in request.headers:
                request.headers["Sec-Ch-Ua"] = (
                    '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
                )
            if "Sec-Ch-Ua-Mobile" not in request.headers:
                request.headers["Sec-Ch-Ua-Mobile"] = "?0"
            if "Sec-Ch-Ua-Platform" not in request.headers:
                request.headers["Sec-Ch-Ua-Platform"] = '"Windows"'
            if "Sec-Fetch-Dest" not in request.headers:
                request.headers["Sec-Fetch-Dest"] = "empty"
            if "Sec-Fetch-Mode" not in request.headers:
                request.headers["Sec-Fetch-Mode"] = "cors"
            if "Sec-Fetch-Site" not in request.headers:
                request.headers["Sec-Fetch-Site"] = "same-origin"

        return None
```

---

## 13. Utilitários Auxiliares

### `instagram_bot/utils.py`

```python
"""
Funções utilitárias para o projeto Sentinela Democrática.

Inclui helpers para manipulação de datas, validação de dados
e diagnóstico de sessão do Instagram.
"""

import json
from datetime import datetime, timezone


def epoch_to_iso(epoch):
    """
    Converte timestamp Unix (epoch) para string ISO 8601.

    O Instagram retorna timestamps como inteiros (segundos desde 1970-01-01).
    O Supabase/PostgreSQL espera strings no formato ISO 8601.

    Args:
        epoch: Timestamp Unix (int ou float) em segundos.

    Returns:
        str: Data/hora no formato ISO 8601 (ex: "2026-04-29T08:00:00+00:00"),
             ou None se o input for inválido.
    """
    if not epoch:
        return None
    try:
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc).isoformat()
    except (ValueError, TypeError, OSError):
        return None


def safe_get(data, path, default=None):
    """
    Acessa com segurança um caminho aninhado em um dicionário.

    Instagram GraphQL retorna dados profundamente aninhados.
    Esta função evita KeyError/TypeError ao acessar caminhos como
    data["data"]["user"]["edge_follow"]["page_info"]["end_cursor"].

    Args:
        data: Dicionário de dados.
        path: Lista de chaves para percorrer (ex: ["data", "user", "id"]).
        default: Valor a retornar se o caminho não existir.

    Returns:
        O valor no caminho especificado, ou `default` se não encontrado.

    Example:
        >>> safe_get({"a": {"b": {"c": 42}}}, ["a", "b", "c"])
        42
        >>> safe_get({"a": {}}, ["a", "b", "c"], "N/A")
        'N/A'
    """
    current = data
    for key in path:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current


def truncate_text(text, max_length=500):
    """
    Trunca um texto para o comprimento máximo, adicionando reticências.

    Útil para logs e para evitar que textos muito longos de comentários
    causem problemas de armazenamento ou exibição.

    Args:
        text: O texto a ser truncado.
        max_length: Comprimento máximo em caracteres (padrão: 500).

    Returns:
        str: O texto truncado com "..." se exceder o limite, ou o texto original.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def validate_session_cookies(cookies):
    """
    Valida se os cookies de sessão contêm os campos necessários
    para fazer requisições autenticadas ao Instagram.

    Args:
        cookies: Dicionário de cookies da sessão.

    Returns:
        tuple: (bool, str) — (True, "") se válido, (False, motivo) se inválido.
    """
    if not cookies:
        return False, "Cookies vazios"

    required = ["sessionid"]
    for key in required:
        if key not in cookies:
            return False, f"Cookie obrigatório ausente: {key}"

    return True, "Cookies válidos"


class InstagramAPIError(Exception):
    """Exceção personalizada para erros da API do Instagram."""

    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self):
        base = super().__str__()
        if self.status_code:
            return f"[HTTP {self.status_code}] {base}"
        return base
```

---

## 14. Docker e Deploy

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegador Chromium para Playwright
RUN playwright install chromium

# Copiar código do projeto
COPY . .

# Criar diretório para sessão persistente
RUN mkdir -p /tmp/ig_session

# Comando padrão: executar o agendador
CMD ["python", "main.py"]
```

### `docker-compose.yml`

```yaml
version: "3.8"

services:
  sentinela:
    build: .
    container_name: sentinela_democratica
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      # Persistir sessão do Instagram entre reinicializações do container
      - ig_session:/tmp/ig_session
      # Persistir logs
      - ./logs:/tmp
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"

volumes:
  ig_session:
```

### Comandos de Deploy

```bash
# Construir a imagem
docker-compose build

# Iniciar o agente em background
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f sentinela

# Parar o agente
docker-compose down

# Reiniciar (após mudança de código)
docker-compose up -d --build
```

---

## 15. Fluxo Completo de Execução

O diagrama abaixo descreve o fluxo completo de uma execução do agente, desde o agendamento até o armazenamento dos dados no Supabase:

```
┌─────────────────────────────────────────┐
│         AGENDADOR (main.py)              │
│  schedule.every().day.at("08:00")        │
│  schedule.every().day.at("20:00")        │
└────────────────┬────────────────────────┘
                 │ 08:00 ou 20:00
                 ▼
┌─────────────────────────────────────────┐
│     FASE 1: LOGIN (Playwright)          │
│                                          │
│  1. Abre instagram.com/accounts/login   │
│  2. Preenche username + password        │
│  3. Aguarda navegação pós-login         │
│  4. Captura cookies (sessionid, csrf)   │
│  5. Fecha o navegador                   │
└────────────────┬────────────────────────┘
                 │ cookies de sessão
                 ▼
┌─────────────────────────────────────────┐
│  FASE 2: PERFIL MONITOR (HTTP API)      │
│                                          │
│  GET /api/v1/users/web_profile_info/    │
│       ?username=monitoramento.discurso   │
│  → Obtém user_id numérico               │
└────────────────┬────────────────────────┘
                 │ user_id
                 ▼
┌─────────────────────────────────────────┐
│  FASE 3: PERFIS SEGUIDOS (GraphQL)      │
│                                          │
│  GET /graphql/query/                     │
│       ?query_hash=HASH_FOLLOWING         │
│       &variables={"id":..., "first":50}  │
│  → Para cada perfil: yield ProfileItem  │
│  → Se has_next_page: paginar            │
└────────────────┬────────────────────────┘
                 │ para cada perfil seguido
                 ▼
┌─────────────────────────────────────────┐
│  FASE 4: POSTS RECENTES (GraphQL)       │
│                                          │
│  GET /graphql/query/                     │
│       ?query_hash=HASH_USER_POSTS        │
│       &variables={"id":..., "first":3}   │
│  → Para cada post: yield PostItem       │
│  → Limite: 3 posts por perfil           │
└────────────────┬────────────────────────┘
                 │ para cada post
                 ▼
┌─────────────────────────────────────────┐
│  FASE 5: COMENTÁRIOS (GraphQL)          │
│                                          │
│  GET /graphql/query/                     │
│       ?query_hash=HASH_COMMENTS          │
│       &variables={"shortcode":...,       │
│                   "first":50}            │
│  → Para cada comentário: yield Comment  │
│  → Se has_next_page E count < 100:      │
│     paginar                             │
│  → Limite: 100 comentários por post     │
└────────────────┬────────────────────────┘
                 │ itens yieldados
                 ▼
┌─────────────────────────────────────────┐
│  PIPELINE SUPABASE (upsert)             │
│                                          │
│  ProfileItem  → profiles  (PK: user_id) │
│  PostItem     → posts     (PK: post_id) │
│  CommentItem  → comments  (PK: id)      │
│                                          │
│  Deduplicação automática via upsert      │
└────────────────┬────────────────────────┘
                 │ dados persistidos
                 ▼
┌─────────────────────────────────────────┐
│           SUPABASE (PostgreSQL)          │
│                                          │
│  Tabela extraction_runs: registro da    │
│  execução (status, contagens, duração)  │
└─────────────────────────────────────────┘
```

---

## 16. Notas e Advertências

### Atualização dos Doc IDs / Query Hashes

Os identificadores `doc_id` e `query_hash` do GraphQL do Instagram **mudam periodicamente** (tipicamente a cada 2-4 semanas) como medida anti-scraping. Quando isso acontecer, o spider retornará erros de resposta vazia ou 403. Para atualizar:

1. Abra o Instagram no navegador com sua conta logada
2. Abra o DevTools (F12) → aba Network
3. Filtre por `graphql/query`
4. Navegue pela plataforma (abra um perfil, role os posts, abra comentários)
5. Copie os novos `doc_id` das requisições capturadas
6. Atualize as constantes no arquivo `instagram_bot/spiders/instagram.py`

### Rate Limiting e Bloqueios

O Instagram é agressivo contra scraping. Medidas implementadas:

| Medida | Configuração | Efeito |
|--------|-------------|--------|
| Delay entre requisições | `DOWNLOAD_DELAY = 3` | 3 segundos entre cada request |
| Randomização do delay | `RANDOMIZE_DOWNLOAD_DELAY = True` | Variação aleatória de 0.5x a 1.5x |
| Requisições concorrentes | `CONCURRENT_REQUESTS = 1` | Apenas 1 request por vez |
| AutoThrottle | `AUTOTHROTTLE_ENABLED = True` | Ajuste automático de velocidade |
| Rotação de User-Agent | `AntiDetectionMiddleware` | Diferente UA por request |
| Contexto persistente | `PLAYWRIGHT_CONTEXTS` | Sessão logada reutilizada |

Se ainda assim ocorrerem bloqueios (HTTP 429 ou login desafiado), considere:

- Aumentar `DOWNLOAD_DELAY` para 5-8 segundos
- Utilizar proxies residenciais rotativos
- Reduzir `CONCURRENT_REQUESTS`
- Adicionar pausas longas (10-30 min) entre perfis

### Alternativa: scrapy-playwright com interceptação de rede

Se os endpoints GraphQL pararem de funcionar completamente, existe uma estratégia alternativa que usa Playwright para **interceptar as respostas da rede** diretamente, sem precisar dos doc_ids:

```python
# No spider, ao abrir uma página do Instagram:
yield scrapy.Request(
    url=f"https://www.instagram.com/{username}/",
    meta={
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_event_handlers": {
            "response": "handle_network_response",
        },
    },
    callback=self.parse_from_intercepted,
)

async def handle_network_response(self, response):
    """Intercepta respostas GraphQL diretamente da rede."""
    if "graphql/query" in response.url:
        try:
            data = await response.json()
            # Processar dados interceptados
            self.captured_data.append(data)
        except Exception:
            pass
```

Esta abordagem é mais lenta (requer renderização completa da página) mas é mais resiliente a mudanças de API, pois captura os dados que o próprio Instagram carrega no navegador.

### Dados Sensíveis

- **Nunca** versione o arquivo `.env` com credenciais reais
- O `sessionid` do Instagram dá acesso total à conta — trate-o como uma senha
- No Supabase, use a `service_role_key` apenas no backend; nunca no frontend
- Considere usar uma conta dedicada para o agente, diferente da conta pessoal

### Compliance e Aspectos Legais

Este sistema foi projetado para monitoramento de discurso público em perfis públicos do Instagram. Antes de utilizá-lo, considere:

- Os Termos de Serviço do Instagram proíbem scraping automatizado
- A LGPD (Lei Geral de Proteção de Dados) aplica-se a dados pessoais de usuários brasileiros
- Comentários em perfis públicos são considerados dados públicos, mas a armazenagem sistemática pode requerer base legal
- Consulte um advogado especializado antes de operar este sistema em escala
