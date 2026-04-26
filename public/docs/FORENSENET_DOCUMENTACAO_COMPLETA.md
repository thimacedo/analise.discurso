# ==============================================================================
# FORENSE NET — Documento Completo do Projeto
# Arquiteto: Z.ai Code | Data: 13/04/2026
# ==============================================================================
#
# Este documento contém TODA a documentação de design, lógica, arquitetura,
# schemas, APIs, componentes e código-fonte do projeto ForenseNet.
# Destinado a agentes externos que precisam entender, replicar ou evoluir o sistema.
#
# ÍNDICE
# ------
# 1. Visão Geral e Metodologia
# 2. Arquitetura do Sistema
# 3. Stack Tecnológica
# 4. Modelo de Dados (Prisma Schema)
# 5. API REST — Endpoints Completos
# 6. Motor de Classificação IA Híbrida
# 7. Componentes Frontend
# 8. Página Principal (page.tsx)
# 9. Seed Data
# 10. Variáveis de Ambiente
# 11. Fluxos de Dados
# 12. Diagrama da Arquitetura Visual
# ==============================================================================


# ==============================================================================
# 1. VISÃO GERAL E METODOLOGIA
# ==============================================================================

ForenseNet é uma plataforma profissional de análise de discurso de ódio em
campanhas políticas brasileiras, baseada na metodologia de Linguística
Forense Digital do Prof. Leonardo Vichi.

PIPELINE PRINCIPAL:
  Instagram Graph API → Coletor → Corpus Builder → Pré-processamento NLP
  → Classificador IA Híbrido → Análise Estatística → Visualizações → Relatório

OBJETIVO:
  - Coletar comentários de perfis políticos no Instagram
  - Classificar automaticamente discurso de ódio em 6 categorias
  - Fornecer dashboard BI profissional para analistas
  - Suportar Active Learning (revisão humana de casos borderline)
  - Gerar alertas automáticos de anomalias

CATEGORIAS DE DISCURSO DE ÓDIO:
  | Categoria   | Severidade Base | Exemplos de Termos                        |
  |-------------|-----------------|-------------------------------------------|
  | Transfobia  | 9/10            | traveco, aberração, mutante, anormal      |
  | Racismo     | 8/10            | macaco, crioulo, selvagem, senzala        |
  | Homofobia   | 7/10            | viado, bicha, sapatão, baitola            |
  | Xenofobia   | 7/10            | nordestino, imigrante, estrangeiro        |
  | Misoginia   | 6/10            | puta, vadia, cadela, lugar de mulher      |
  | Genérico    | 5/10            | lixo, ladrão, escória, corja, parasita    |

CONFORMIDADE:
  - LGPD: Dados tratados apenas para fins acadêmicos/pesquisa
  - Classificação automática DEVE ser validada por análise humana
  - Não utilizar para vigilância massiva


# ==============================================================================
# 2. ARQUITETURA DO SISTEMA
# ==============================================================================

ESTRUTURA DE ARQUIVOS:
  forensenet/
  ├── prisma/
  │   ├── schema.prisma          # Schema do banco de dados
  │   └── seed.ts                # Script de população com dados realistas
  ├── src/
  │   ├── app/
  │   │   ├── layout.tsx         # Layout raiz (pt-BR, fontes Geist)
  │   │   ├── page.tsx           # Dashboard principal (4 abas)
  │   │   ├── globals.css        # Variáveis CSS + tema claro/escuro
  │   │   └── api/
  │   │       ├── analyze/route.ts            # POST: Classificação IA
  │   │       ├── candidates/route.ts         # GET: Candidatos com stats
  │   │       ├── comments/route.ts           # GET: Comentários filtrados
  │   │       ├── comments/review/route.ts    # PATCH: Revisão humana
  │   │       ├── alerts/route.ts             # GET/PATCH: Alertas
  │   │       ├── pipeline/status/route.ts    # GET: Saúde do pipeline
  │   │       ├── pipeline/events/route.ts    # GET: Stream de eventos
  │   │       ├── dashboard/stats/route.ts    # GET: KPIs agregados
  │   │       ├── dashboard/categories/route.ts # GET: Stats por categoria
  │   │       └── dashboard/timeline/route.ts   # GET: Série temporal
  │   ├── components/
  │   │   ├── ui/               # Componentes shadcn/ui (50+ componentes)
  │   │   └── forensenet/
  │   │       ├── ai-analyzer.tsx        # Classificador IA interativo
  │   │       ├── stats-cards.tsx        # 8 KPI cards
  │   │       ├── candidate-cards.tsx    # Grid de candidatos monitorados
  │   │       ├── category-chart.tsx     # Barras horizontais por categoria
  │   │       ├── severity-chart.tsx     # Donut de severidade
  │   │       ├── timeline-chart.tsx     # Área temporal (com select período)
  │   │       ├── comments-table.tsx     # Tabela com filtros + paginação
  │   │       ├── pipeline-view.tsx      # Saúde + jobs + stream eventos
  │   │       └── alerts-panel.tsx       # Painel de alertas com ações
  │   ├── hooks/
  │   │   ├── use-toast.ts
  │   │   └── use-mobile.ts
  │   └── lib/
  │       ├── db.ts              # Singleton PrismaClient
  │       └── utils.ts           # cn() helper
  ├── db/
  │   └── custom.db             # Banco SQLite
  └── public/
      └── forensenet-logo.png   # Logo gerado por IA

DIAGRAMA DA ARQUITETURA VISUAL (Pipeline):

  [ Perfis Públicos Instagram ]
            │
            ▼
  [ Scraper Cluster (Playwright + Proxies) ]
            │
            ▼
  [ Message Broker (Redis/Celery) ] ──> Fila: raw_comments
            │
            ▼
  [ Worker de Processamento (spaCy/NLP) ]
            │
            ▼
  [ Message Broker (Redis) ] ──> Fila: to_classify
            │
            ▼
  [ Modelo IA (LLM + Keywords Híbrido) ]
            │
            ▼
  [ Banco de Dados (SQLite/PostgreSQL) ]
            │
            ├──────────────────────────────────┐
            ▼                                  ▼
  [ Next.js API Routes ]           [ Dashboard React (BI) ]
            │
            ▼
  [ Alertas (Slack/Discord/Grafana) ]


# ==============================================================================
# 3. STACK TECNOLÓGICA
# ==============================================================================

CORE:
  - Framework:    Next.js 16 (App Router)
  - Linguagem:    TypeScript 5
  - Styling:      Tailwind CSS 4 + shadcn/ui (New York style)
  - Database:     Prisma ORM + SQLite (produção: PostgreSQL)
  - Charts:       Recharts 2.15
  - Icons:        Lucide React 0.525

IA / ML:
  - LLM SDK:      z-ai-web-dev-sdk 0.0.17 (backend only!)
  - Classificação: Híbrida (LLM contextual + Dicionário de palavras-chave)
  - Active Learning: needsReview flag para revisão humana

STATE MANAGEMENT:
  - Client state:  useState/useCallback (React hooks)
  - Auto-refresh:  setInterval (60s)

COMPONENTES UI (shadcn/ui - todos em src/components/ui/):
  accordion, alert, alert-dialog, avatar, badge, button, calendar,
  card, carousel, chart, checkbox, collapsible, command, context-menu,
  dialog, drawer, dropdown-menu, form, hover-card, input, input-otp,
  label, menubar, navigation-menu, pagination, popover, progress,
  radio-group, resizable, scroll-area, select, separator, sheet,
  sidebar, skeleton, slider, sonner, switch, table, tabs, textarea,
  toast, toaster, toggle, toggle-group, tooltip


# ==============================================================================
# 4. MODELO DE DADOS (Prisma Schema)
# ==============================================================================

```prisma
// ForenseNet - Análise de Discurso de Ódio em Campanhas Políticas

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

// ==========================================
// CORE ENTITIES
// ==========================================

model Candidate {
  id          String   @id @default(cuid())
  name        String   // e.g. "Jair Bolsonaro"
  username    String   @unique // Instagram handle
  party       String   // e.g. "PL", "PT", "MDB"
  position    String   // e.g. "Presidente", "Senador", "Deputado"
  state       String?  // e.g. "SP", "RJ"
  avatarUrl   String?
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  comments    Comment[]
  scrapingJobs ScrapingJob[]
}

model Comment {
  id              String   @id @default(cuid())
  candidateId     String
  candidate       Candidate @relation(fields: [candidateId], references: [id], onDelete: Cascade)

  // Raw data from scraping
  sourceId        String?  // Original post/comment ID from Instagram
  sourceUrl       String?  // Link to original post
  postCaption     String?  // Caption of the post where comment was found
  authorUsername   String   // Username of commenter
  authorName      String?  // Display name of commenter
  text            String   // The actual comment text
  likeCount       Int      @default(0)
  replyCount      Int      @default(0)
  isReply         Boolean  @default(false)
  parentCommentId String?  // If this is a reply

  // Processing metadata
  isProcessed     Boolean  @default(false)
  processedText   String?  // Cleaned/normalized text
  language        String   @default("pt-BR")
  tokens          String?  // JSON array of tokens

  // Timestamps
  publishedAt     DateTime? // When the comment was originally posted
  scrapedAt       DateTime  @default(now())
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt

  classification  Classification?
}

model Classification {
  id              String   @id @default(cuid())
  commentId       String   @unique
  comment         Comment  @relation(fields: [commentId], references: [id], onDelete: Cascade)

  // Classification results
  isHateSpeech    Boolean
  confidence      Float    // 0.0 to 1.0
  category        String?  // "racismo", "homofobia", "misoginia", "xenofobia", "transfobia", "generico"
  severity        Int      @default(0) // 0-10 scale
  sentiment       String?  // "positive", "negative", "neutral"
  sentimentScore  Float?   // -1.0 to 1.0

  // AI details
  classifierType  String   // "keyword", "llm", "hybrid"
  classifierModel String?  // e.g. "claude-3", "bertimbau"
  reasoning       String?  // AI explanation for the classification
  keywords        String?  // JSON array of detected keywords

  // Active Learning
  needsReview     Boolean  @default(false) // Flagged for human review
  reviewedBy      String?  // Reviewer ID
  reviewedAt      DateTime?
  reviewDecision  String?  // "confirmed", "overturned", "modified"

  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}

// ==========================================
// PIPELINE & INFRASTRUCTURE
// ==========================================

model ScrapingJob {
  id              String   @id @default(cuid())
  candidateId     String
  candidate       Candidate @relation(fields: [candidateId], references: [id], onDelete: Cascade)

  status          String   @default("pending") // "pending", "running", "completed", "failed"
  targetType      String   @default("comments") // "comments", "posts", "profile"
  targetUrl       String?
  itemsFound      Int      @default(0)
  itemsProcessed  Int      @default(0)
  errorCount      Int      @default(0)
  lastError       String?

  startedAt       DateTime?
  completedAt     DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  events          PipelineEvent[]
}

model PipelineEvent {
  id              String   @id @default(cuid())
  jobId           String?
  job             ScrapingJob? @relation(fields: [jobId], references: [id], onDelete: SetNull)

  eventType       String   // "scrape_start", "scrape_complete", "classify_start", "classify_complete", "alert", "error"
  source          String   // "scraper", "processor", "classifier", "pipeline", "system"
  message         String
  data            String?  // JSON payload for additional data
  level           String   @default("info") // "info", "warning", "error", "critical"

  createdAt       DateTime @default(now())
}

model Alert {
  id              String   @id @default(cuid())
  type            String   // "scraper_blocked", "high_hate_rate", "api_down", "model_drift"
  severity        String   @default("warning") // "info", "warning", "critical"
  message         String
  isRead          Boolean  @default(false)
  isResolved      Boolean  @default(false)
  resolvedAt      DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}

model DashboardCache {
  id              String   @id @default(cuid())
  cacheKey        String   @unique
  data            String   // JSON serialized data
  expiresAt       DateTime
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}
```

RELACIONAMENTOS:
  Candidate 1──N Comment (via candidateId)
  Comment   1──1 Classification (via commentId, unique)
  Candidate 1──N ScrapingJob (via candidateId)
  ScrapingJob 1──N PipelineEvent (via jobId, opcional)


# ==============================================================================
# 5. API REST — ENDPOINTS COMPLETOS
# ==============================================================================

Todos os endpoints usam caminhos relativos (Next.js API Routes).
Base URL implícito: http://localhost:3000

───────────────────────────────────────────────────────────────────────────────
5.1 POST /api/analyze — Classificação IA Híbrida
───────────────────────────────────────────────────────────────────────────────

REQUEST:
  {
    "text": "Bando de macacos governando esse país",   // obrigatório, max 5000 chars
    "candidateName": "Flávio Bolsonaro"                 // opcional, contexto para LLM
  }

RESPONSE (200):
  {
    "text": "Bando de macacos governando esse país",
    "classification": {
      "isHateSpeech": true,
      "category": "racismo",
      "severity": 8,
      "confidence": 0.93,
      "sentiment": "negative",
      "reasoning": "O termo 'bando de macacos' é uma comparação desonrosa...",
      "classifierType": "hybrid",           // "hybrid" | "keyword"
      "matchedKeywords": ["macaco"],
      "needsReview": false                   // true se confidence < 0.65
    }
  }

ERRORS:
  400: { "error": "Text is required" }
  400: { "error": "Text too long (max 5000 characters)" }
  500: { "error": "Failed to analyze text" }

LÓGICA INTERNA:
  1. classifyWithKeywords(text) → match local de dicionário (instantâneo)
  2. LLM classification via z-ai-web-dev-sdk → análise contextual
  3. Hybrid merge:
     - isHateSpeech = LLM OR Keywords (basta um detectar)
     - category = LLM prevalece, fallback keyword, fallback "generico"
     - severity = max(LLM, keyword)
     - confidence = média quando ambos concordam, LLM sozinho quando discorda,
       inversão (1-P) para neutros
     - needsReview = true quando isHateSpeech && confidence < 0.65
  4. Se LLM falhar, retorna resultado keyword-only com confidence reduzida

───────────────────────────────────────────────────────────────────────────────
5.2 GET /api/candidates — Lista candidatos com estatísticas
───────────────────────────────────────────────────────────────────────────────

RESPONSE (200):
  {
    "candidates": [
      {
        "id": "cl_xxx",
        "name": "Marina da Silva",
        "username": "marinasilva.oficial",
        "party": "PSOL",
        "position": "Senadora",
        "state": "AC",
        "avatarUrl": null,
        "isActive": true,
        "commentCount": 28,
        "hateSpeechCount": 7,
        "hateSpeechRate": 25.0,           // %
        "avgSeverity": 6.8,
        "topCategory": "racismo",         // categoria mais frequente
        "latestJobStatus": "completed"    // status do último scraping job
      }
    ]
  }

QUERY INTERNA:
  - findMany Candidate com _count.comments
  - Raw query: hateSpeechCount, avgSeverity agrupados por candidateId
  - Raw query: topCategory via ROW_NUMBER() OVER (PARTITION BY candidateId)

───────────────────────────────────────────────────────────────────────────────
5.3 GET /api/comments — Comentários com filtros e paginação
───────────────────────────────────────────────────────────────────────────────

QUERY PARAMS:
  page=1                    // página atual (default: 1)
  pageSize=20               // itens por página (max: 100)
  candidateId=cl_xxx        // filtrar por candidato
  isHateSpeech=true         // filtrar ódio/neutro
  category=racismo          // filtrar por categoria
  needsReview=true          // filtrar pendentes de revisão
  search=termo              // buscar no texto
  sortBy=date               // "date" | "severity" | "confidence"
  sortOrder=desc            // "asc" | "desc"

RESPONSE (200):
  {
    "data": [
      {
        "id": "cl_xxx",
        "text": "...",
        "authorUsername": "joao_silva23",
        "likeCount": 5,
        "candidate": { "id": "...", "name": "...", "party": "PT" },
        "classification": {
          "isHateSpeech": true,
          "confidence": 0.93,
          "category": "racismo",
          "severity": 8,
          "sentiment": "negative",
          "classifierType": "hybrid",
          "reasoning": "...",
          "needsReview": false
        },
        "publishedAt": "2025-11-15T...",
        "createdAt": "2025-11-15T..."
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 220,
      "totalPages": 11,
      "hasNext": true,
      "hasPrev": false
    }
  }

───────────────────────────────────────────────────────────────────────────────
5.4 PATCH /api/comments/review — Revisão humana (Active Learning)
───────────────────────────────────────────────────────────────────────────────

REQUEST:
  {
    "commentId": "cl_xxx",           // obrigatório
    "reviewDecision": "confirmed",   // "confirmed" | "overturned" | "modified"
    "reviewedBy": "analyst"          // opcional, default: "analyst"
  }

RESPONSE (200):
  {
    "success": true,
    "classification": { /* objeto Classification atualizado */ }
  }

───────────────────────────────────────────────────────────────────────────────
5.5 GET /api/dashboard/stats — KPIs agregados do dashboard
───────────────────────────────────────────────────────────────────────────────

RESPONSE (200):
  {
    "totalComments": 220,
    "hateSpeechCount": 55,
    "hateSpeechRate": 25.0,
    "activeCandidates": 8,
    "pendingReview": 26,
    "alertsUnread": 4,
    "recentJobs": 0,
    "avgConfidence": 0.8914,
    "categoryBreakdown": {
      "generico": 9,
      "homofobia": 9,
      "misoginia": 9,
      "racismo": 10,
      "transfobia": 9,
      "xenofobia": 9
    },
    "severityDistribution": {
      "0-3": 167,
      "4-6": 11,
      "7-10": 42
    }
  }

───────────────────────────────────────────────────────────────────────────────
5.6 GET /api/dashboard/categories — Estatísticas por categoria
───────────────────────────────────────────────────────────────────────────────

RESPONSE (200):
  {
    "categories": [
      {
        "category": "racismo",
        "count": 10,
        "avgSeverity": 7.5,
        "avgConfidence": 0.91,
        "sentimentDistribution": { "negative": 8, "neutral": 2 },
        "topKeywords": ["macaco", "senzala", "cota"]
      }
    ]
  }

───────────────────────────────────────────────────────────────────────────────
5.7 GET /api/dashboard/timeline — Série temporal
───────────────────────────────────────────────────────────────────────────────

QUERY PARAMS:
  period=30d               // "7d" | "30d" | "90d" | "all"
  candidateId=cl_xxx       // filtrar por candidato

RESPONSE (200):
  {
    "period": "30d",
    "data": [
      {
        "date": "2025-10-15",
        "totalComments": 12,
        "hateSpeechCount": 3,
        "avgSeverity": 6.8,
        "topCategory": "racismo"
      }
    ]
  }

───────────────────────────────────────────────────────────────────────────────
5.8 GET /api/alerts — Alertas do sistema
───────────────────────────────────────────────────────────────────────────────

RESPONSE (200):
  {
    "alerts": [
      {
        "id": "cl_xxx",
        "type": "scraper_blocked",
        "severity": "warning",
        "message": "Scraper bloqueado pelo Instagram...",
        "isRead": false,
        "isResolved": false,
        "resolvedAt": null,
        "createdAt": "2026-04-10T...",
        "updatedAt": "2026-04-10T..."
      }
    ]
  }

PATCH /api/alerts — Marcar como lido/resolvido
  Body: { "id": "cl_xxx", "isRead": true }
  Body: { "ids": ["cl_xxx", "cl_yyy"], "isResolved": true }

───────────────────────────────────────────────────────────────────────────────
5.9 GET /api/pipeline/status — Saúde e status do pipeline
───────────────────────────────────────────────────────────────────────────────

RESPONSE (200):
  {
    "activeJobs": [
      {
        "id": "cl_xxx",
        "candidateId": "cl_yyy",
        "candidateName": "Ciro Gomes",
        "targetType": "comments",
        "itemsFound": 250,
        "itemsProcessed": 180,
        "startedAt": "2026-04-13T..."
      }
    ],
    "recentEvents": [ ... ],     // últimos 50 eventos
    "jobStats": {
      "completed": 6,
      "failed": 2,
      "running": 2,
      "pending": 2
    },
    "systemHealth": {
      "status": "degraded",     // "healthy" | "degraded" | "critical"
      "lastError": "Rate limit exceeded...",
      "unresolvedAlerts": 4,
      "criticalAlerts": 2
    }
  }

LÓGICA DE SAÚDE:
  - critical: criticalAlerts > 0
  - degraded: unresolvedAlerts > 3 || failedJobs > completedJobs
  - healthy: caso contrário

───────────────────────────────────────────────────────────────────────────────
5.10 GET /api/pipeline/events — Stream de eventos
───────────────────────────────────────────────────────────────────────────────

QUERY PARAMS:
  limit=50                  // max 200

RESPONSE (200):
  {
    "events": [
      {
        "id": "cl_xxx",
        "eventType": "scrape_complete",
        "source": "scraper",
        "message": "Scraping concluído para Ciro Gomes: 250 itens",
        "level": "info",
        "createdAt": "2026-04-13T...",
        "jobId": "cl_yyy",
        "job": {
          "id": "cl_yyy",
          "status": "completed",
          "candidate": { "name": "Ciro Gomes" }
        }
      }
    ]
  }


# ==============================================================================
# 6. MOTOR DE CLASSIFICAÇÃO IA HÍBRIDA
# ==============================================================================

6.1 DICIONÁRIO DE PALAVRAS-CHAVE (classifyWithKeywords)
─────────────────────────────────────────────────────────

O dicionário é executado PRIMEIRO, de forma síncrona e local (zero latência).
Para cada termo encontrado, registra categoria e severidade base.

```typescript
const HATE_KEYWORDS: Record<string, { terms: string[]; severity: number }> = {
  transfobia: {
    severity: 9,
    terms: ['traveco', 'aberração', 'mutante', 'anormal', 'doente',
            'falsa mulher', 'pronome', 'ideologia de gênero'],
  },
  racismo: {
    severity: 8,
    terms: ['macaco', 'crioulo', 'selvagem', 'escravo', 'senzala',
            'primitivo', 'cota', 'preto'],
  },
  homofobia: {
    severity: 7,
    terms: ['viado', 'bicha', 'sapatão', 'baitola', 'boiola',
            'viadinho', 'gayzista', 'agenda gay'],
  },
  xenofobia: {
    severity: 7,
    terms: ['nordestino', 'baiano', 'paraíba', 'migrante', 'invasor',
            'favelado', 'imigrante', 'estrangeiro', 'venezuelano', 'haitiano'],
  },
  misoginia: {
    severity: 6,
    terms: ['puta', 'vadia', 'cadela', 'vagabunda', 'lugar de mulher',
            'sexo frágil', 'chorona', 'emotiva'],
  },
  generico: {
    severity: 5,
    terms: ['lixo', 'ladrão', 'escória', 'corja', 'desgraçado',
            'parasita', 'cadeia'],
  },
};
```

ALGORITMO:
  1. text.toLowerCase()
  2. Para cada categoria, para cada termo:
     - Se termo existe no texto (substring match)
     - Marca isHateSpeech = true
     - Registra termo em matchedKeywords
     - Se severity da categoria > maxSeverity atual, atualiza categoria
  3. Retorna { isHateSpeech, category, severity, matchedKeywords }

6.2 LLM CLASSIFICATION (z-ai-web-dev-sdk)
──────────────────────────────────────────

Executado em SEGUNDO lugar, via chamada à API do LLM.

SYSTEM PROMPT:
```
Você é um especialista em Linguística Forense Digital e análise de discurso
de ódio no contexto político brasileiro. Sua tarefa é classificar comentários
de redes sociais direcionados a figuras políticas brasileiras.

Classifique o texto seguindo estas categorias:
- "racismo": Discurso discriminatório baseado em raça/cor
- "homofobia": Discurso discriminatório contra LGBTQIA+
- "transfobia": Discurso discriminatório contra pessoas trans
- "misoginia": Discurso discriminatório contra mulheres
- "xenofobia": Discurso discriminatório contra estrangeiros/imigrantes
  ou contra pessoas de outras regiões do Brasil
- "generico": Discurso de ódio genérico, ameaças, insultos graves
- "neutro": Não é discurso de ódio (crítica política legítima, apoio, opinião civil)

Responda APENAS com JSON válido no formato:
{
  "is_hate_speech": boolean,
  "category": "racismo" | "homofobia" | "transfobia" | "misoginia" |
              "xenofobia" | "generico" | null,
  "confidence": 0.0-1.0,
  "severity": 0-10,
  "sentiment": "positive" | "negative" | "neutral",
  "reasoning": "breve justificativa em português"
}
```

USER MESSAGE (com contexto):
  "Analise este comentário direcionado ao político "{candidateName}":\n\n"{text}"
  —ou—
  "Analise este comentário de rede social:\n\n"{text}"

SDK CALL:
```typescript
const zai = await ZAI.create();
const completion = await zai.chat.completions.create({
  messages: [
    { role: 'assistant', content: SYSTEM_PROMPT },
    { role: 'user', content: userMessage },
  ],
  thinking: { type: 'disabled' },
});
const rawResponse = completion.choices[0]?.message?.content || '';
const jsonMatch = rawResponse.match(/\{[\s\S]*\}/);
llmResult = JSON.parse(jsonMatch[0]);
```

6.3 HYBRID MERGE (Fusão)
─────────────────────────

A fusão combina os dois resultados, dando preferência ao LLM para categoria
e usando OR para detecção de ódio (basta um detectar):

```
isHateSpeech = LLM.is_hate_speech OR Keyword.isHateSpeech

category = isHateSpeech
  ? (LLM.category || Keyword.category || "generico")
  : null

severity = isHateSpeech
  ? max(LLM.severity, Keyword.severity)
  : 0

confidence:
  - Ambos concordam ódio: média(LLM.confidence, 0.85) → boost
  - LLM diz ódio, keyword não: LLM.confidence
  - Ambos dizem neutro: 1 - LLM.confidence → invertido (clamp 0.6-1.0)
  - Apenas keyword: 0.7 (ódio) ou 0.6 (neutro)

needsReview = isHateSpeech && confidence < 0.65

classifierType = LLM disponível ? "hybrid" : "keyword"
```

6.4 ACTIVE LEARNING
────────────────────

Comentários classificados como ódio com confidence < 0.65 são marcados com
needsReview = true. Esses casos são encaminhados para revisão humana:

  PATCH /api/comments/review
  {
    "commentId": "...",
    "reviewDecision": "confirmed" | "overturned" | "modified"
  }

Os dados revisados podem ser usados futuramente para fine-tuning do modelo.


# ==============================================================================
# 7. COMPONENTES FRONTEND
# ==============================================================================

Todos os componentes são 'use client' e usam shadcn/ui + Lucide icons.

7.1 StatsCards (stats-cards.tsx)
────────────────────────────────
PROPS: { stats: DashboardStats | null }

8 KPI cards em grid 2x4:
  1. Total de Comentários (MessageSquare, emerald)
  2. Discurso de Ódio (AlertTriangle, red) — mostra % do total
  3. Candidatos Ativos (Users, blue)
  4. Revisão Pendente (Eye, amber) — "Active Learning"
  5. Alertas Não Lidos (Bell, orange)
  6. Jobs Recentes (Activity, violet) — "Últimas 24h"
  7. Confiança Média (Shield, teal)
  8. Severidade Alta (TrendingUp, rose) — "Score 7-10"

Skeleton loading quando stats = null.

7.2 CategoryChart (category-chart.tsx)
──────────────────────────────────────
PROPS: { categories: CategoryStats[] | null }

Gráfico de barras horizontal (Recharts BarChart, layout="vertical"):
  - Eixo Y: nome da categoria
  - Eixo X: contagem
  - Cada barra com cor própria (Cell)
  - Tooltip: ocorrências, severidade média, confiança média
  - Abaixo: lista de top keywords por categoria

Cores:
  racismo: hsl(0,72%,51%), homofobia: hsl(280,67%,52%),
  misoginia: hsl(330,65%,48%), xenofobia: hsl(35,85%,50%),
  transfobia: hsl(260,60%,55%), generico: hsl(200,15%,45%)

7.3 SeverityChart (severity-chart.tsx)
──────────────────────────────────────
PROPS: { distribution: { '0-3': number, '4-6': number, '7-10': number } | null }

Donut chart (Recharts PieChart):
  - 0-3: Baixa (hsl(160,60%,45%))
  - 4-6: Média (hsl(45,85%,50%))
  - 7-10: Alta (hsl(0,72%,51%))
  - innerRadius=45, outerRadius=70, paddingAngle=3
  - Legenda abaixo com contagens

7.4 TimelineChart (timeline-chart.tsx)
──────────────────────────────────────
PROPS: { data: TimelineRow[] | null, onPeriodChange: (period: string) => void }

Gráfico de área empilhada (Recharts AreaChart):
  - 2 áreas: totalComments (verde) + hateSpeechCount (vermelho)
  - Select de período: 7d, 30d, 90d, Tudo
  - Eixo X formatado como DD/MM
  - CartesianGrid tracejado

7.5 CandidateCards (candidate-cards.tsx)
─────────────────────────────────────────
PROPS: { candidates: CandidateWithStats[] | null }

Grid 1/2/4 colunas de cards por candidato:
  - Nome + username + Badge do partido (cores por partido)
  - Cargo + Estado
  - 3 stats: Comentários, Ódio, Severidade Média
  - Barra de progresso da taxa de ódio (verde<15%, amber 15-30%, red>30%)
  - Footer: top category + status do último job

Cores de partido:
  PT: red, PL: green, PSOL: yellow, MDB: blue,
  PDT: rose, UNIÃO: orange, PSD: teal, REPUBLICANOS: gray

7.6 CommentsTable (comments-table.tsx)
───────────────────────────────────────
PROPS: nenhuma (faz fetch interno)

Tabela com filtros + paginação:
  Filtros: busca textual, ódio (todos/com/sem), categoria, revisão
  Colunas: Status (ícone), Comentário, Autor, Candidato (badge partido),
            Categoria (badge colorido), Severidade (colorido), Confiança,
            Revisão (ícone olho)
  ScrollArea max-h-500px, paginação com prev/next

7.7 PipelineView (pipeline-view.tsx)
────────────────────────────────────
PROPS: nenhuma (faz fetch interno, auto-refresh 30s)

3 seções:
  1. Saúde do Sistema: badge (healthy/degraded/critical),
     último erro, alertas abertos, alertas críticos
  2. Status dos Jobs: grid 2x2 (completed/failed/running/pending)
     + diagrama visual do pipeline (Scraper→Fila→NLP→IA→DB)
  3. Stream de Eventos: lista scrollável dos últimos 50 eventos
     com ícones por tipo (Zap, CheckCircle2, XCircle, AlertTriangle)

7.8 AlertsPanel (alerts-panel.tsx)
──────────────────────────────────
PROPS: nenhuma (faz fetch interno)

Lista de alertas com ações:
  - Ícone por severidade (AlertOctagon/AlertTriangle/Info)
  - Tipo traduzido (scraper_blocked → "Scraper Bloqueado")
  - Marcar como lido (X) ou resolver (Check)
  - "Resolver Todos" em bulk
  - Ring animado para não lidos

7.9 AiAnalyzer (ai-analyzer.tsx)
────────────────────────────────
PROPS: nenhuma (faz fetch interno)

Card com borda gradiente (rose→violet→cyan):
  INPUT:
    - Textarea para colar comentário
    - Select de candidato (opcional, do /api/candidates)
    - Botão "Analisar" com Sparkles icon
  OUTPUT:
    - Veredicto: "DISCURSO DE ÓDIO" (red) ou "NEUTRO" (green)
    - Badge de categoria (cor por tipo)
    - Badge de tipo de classificador (Híbrido/Palavras-chave)
    - Badge "Revisão Necessária" (Active Learning)
    - Barra de severidade (0-10, cor por faixa)
    - Barra de confiança (0-100%, cor por faixa)
    - Badge de sentimento (Negativo/Positivo/Neutro)
    - Seção "JUSTIFICATIVA DA IA" em itálico
    - Seção "PALAVRAS-CHAVE DETECTADAS" com badges
    - Footer: "Metodologia: Prof. Leonardo Vichi"


# ==============================================================================
# 8. PÁGINA PRINCIPAL (page.tsx)
# ==============================================================================

'use client' — componente principal do dashboard.

ESTRUTURA:
  <div min-h-screen flex flex-col>
    <header sticky top-0 z-50>
      Logo + título + badges (Pipeline Ativo, Revisão) + botão Atualizar
    </header>

    <main flex-1>
      <Tabs 4 abas>
        ┌──────────────┬──────────────┬──────────────┬──────────────┐
        │  Dashboard   │  Análise IA  │ Comentários  │   Pipeline   │
        └──────────────┴──────────────┴──────────────┴──────────────┘

        TAB Dashboard:
          StatsCards (8 KPIs)
          grid 2:1 [CategoryChart | SeverityChart]
          TimelineChart (com select de período)
          CandidateCards (grid de candidatos)

        TAB Análise IA:
          grid 1:1 [AiAnalyzer | SeverityChart + AlertsPanel]

        TAB Comentários:
          CommentsTable

        TAB Pipeline:
          Diagrama visual da arquitetura (emojis + badges coloridos)
          PipelineView
      </Tabs>
    </main>

    <footer sticky bottom mt-auto>
      ForenseNet — Metodologia: Prof. Leonardo Vichi — LGPD compliant
    </footer>
  </div>

DATA FLOW:
  - useEffect → fetchDashboardData() na montagem
  - fetch paralelo: /api/dashboard/stats, /api/candidates,
    /api/dashboard/categories, /api/dashboard/timeline
  - Auto-refresh a cada 60 segundos
  - Botão "Atualizar" com RefreshCw animado

TIPOS TYPESCRIPT:
  DashboardStats, CandidateWithStats, CategoryStats, TimelineRow


# ==============================================================================
# 9. SEED DATA
# ==============================================================================

Script: prisma/seed.ts
Comando: bun run prisma/seed.ts

DADOS CRIADOS:
  | Entidade          | Quantidade | Detalhes                                    |
  |-------------------|------------|---------------------------------------------|
  | Candidates        | 8          | PSOL, MDB, PDT, UNIÃO, PSD, PL, PT, REP    |
  | Comments          | 220        | 165 neutros, 55 ódio (~25%)                 |
  | Classifications   | 220        | 24 precisam revisão (needsReview=true)      |
  | Scraping Jobs     | 12         | 6 completed, 2 running, 2 failed, 2 pending |
  | Pipeline Events   | 35         | Todos tipos e níveis                        |
  | Alerts            | 8          | 4 resolvidos, 4 abertos                     |

DISTRIBUIÇÃO DE ÓDIO POR CATEGORIA:
  racismo: 10, homofobia: 9, misoginia: 9,
  xenofobia: 9, transfobia: 9, generico: 9

TIPOS DE CLASSIFICADOR:
  llm: 88, hybrid: 73, keyword: 59

CANDIDATOS:
  1. Marina da Silva (PSOL/AC)
  2. Ricardo Nunes (MDB/SP)
  3. Ciro Gomes (PDT/CE)
  4. Romeu Zema (UNIÃO/MG)
  5. Simone Tebet (PSD/MS)
  6. Flávio Bolsonaro (PL/RJ)
  7. Fernando Haddad (PT/SP)
  8. Marcos Pereira (REPUBLICANOS/SP)

CARACTERÍSTICAS DOS DADOS:
  - Comentários em português brasileiro realista
  - Mix de confidence (maioria 0.85+, alguns borderline 0.4-0.6)
  - Alguns com revisão humana (reviewDecision)
  - Datas: Oct 2025 - Mar 2026 (comentários), últimos 7 dias (eventos)
  - Alertas: scraper_blocked, high_hate_rate, api_down, model_drift
  - Jobs com mensagens de erro realistas (rate limit, captcha, timeout)


# ==============================================================================
# 10. VARIÁVEIS DE AMBIENTE
# ==============================================================================

DATABASE_URL=file:./db/custom.db       # SQLite (produção: postgresql://...)

Para migração futura a PostgreSQL, basta trocar a URL e o provider no
schema.prisma de "sqlite" para "postgresql".


# ==============================================================================
# 11. FLUXOS DE DADOS
# ==============================================================================

11.1 FLUXO DE CLASSIFICAÇÃO EM TEMPO REAL (Análise IA)
───────────────────────────────────────────────────────

  Usuário digita comentário
         │
         ▼
  Frontend: AiAnalyzer → POST /api/analyze { text, candidateName }
         │
         ▼
  Backend: classifyWithKeywords(text) → resultado local instantâneo
         │
         ▼
  Backend: ZAI.create() → chat.completions.create() → LLM contextual
         │
         ▼
  Backend: Hybrid merge → resultado final
         │
         ▼
  Frontend: Exibe veredicto + categoria + severidade + confiança +
            justificativa + keywords + needsReview

11.2 FLUXO DE DADOS DO DASHBOARD
─────────────────────────────────

  page.tsx (mount)
         │
         ├── GET /api/dashboard/stats ──→ StatsCards
         ├── GET /api/candidates ──────→ CandidateCards
         ├── GET /api/dashboard/categories → CategoryChart
         └── GET /api/dashboard/timeline ──→ TimelineChart
         │
         (auto-refresh a cada 60s)

11.3 FLUXO DE REVISÃO HUMANA (Active Learning)
───────────────────────────────────────────────

  CommentsTable mostra comentarios com needsReview=true (ícone olho)
         │
         ▼
  Analista clica "Confirmar/Reverter/Modificar"
         │
         ▼
  PATCH /api/comments/review { commentId, reviewDecision }
         │
         ▼
  Backend: Classification.needsReview = false,
           reviewedBy, reviewedAt, reviewDecision atualizados

11.4 FLUXO DE ALERTAS
──────────────────────

  Sistema detecta anomalia (scraper bloqueado, taxa de ódio alta, etc.)
         │
         ▼
  Cria Alert no banco
         │
         ▼
  AlertsPanel: GET /api/alerts → lista alertas
         │
         ▼
  PATCH /api/alerts { id, isRead: true / isResolved: true }

11.5 FLUXO DO PIPELINE
───────────────────────

  PipelineView: GET /api/pipeline/status (auto-refresh 30s)
         │
         ├── activeJobs: jobs com status "running"
         ├── recentEvents: últimos 50 PipelineEvents
         ├── jobStats: count por status
         └── systemHealth: healthy | degraded | critical


# ==============================================================================
# 12. DIAGRAMA DA ARQUITETURA VISUAL (renderizado no Pipeline tab)
# ==============================================================================

  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  📱      │     │  🕷️      │     │  📋      │     │  ⚙️      │
  │  Perfis  │ ──→ │  Scraper │ ──→ │  Fila    │ ──→ │  NLP     │
  │ Instagram│     │ Playwright│     │raw_comm. │     │ spaCy    │
  └──────────┘     │ +Proxies │     └──────────┘     └──────────┘
                   └──────────┘
                                                      ┌──────────┐
                                                      │  🤖      │
                                                   ──→│  IA      │
                                                      │LLM+Keyw.│
                                                      └──────────┘
                                                            │
                   ┌──────────┐                             │
                   │  🗄️      │ ◄───────────────────────────┘
                   │  DB      │
                   │PostgreSQL│
                   └──────────┘
                      │       │
          ┌───────────┘       └───────────┐
          ▼                               ▼
   ┌──────────────┐              ┌──────────────┐
   │  FastAPI     │              │  Dashboard   │
   │  API Routes  │              │  React (BI)  │
   └──────────────┘              └──────────────┘
          │
          ▼
   ┌──────────────┐
   │  Alertas     │
   │  Grafana/    │
   │  Slack       │
   └──────────────┘


# ==============================================================================
# FIM DO DOCUMENTO
# ==============================================================================
