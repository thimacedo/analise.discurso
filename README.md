# 🛡️ Sentinela Democrática — Inteligência Situacional v18.0

Pipeline profissional e unificado para coleta escalável, análise linguística forense e visualização de discurso de ódio e tendências políticas, baseado no **Protocolo PASA** (Proprietário).

---

## 📋 Arquitetura Atual (Backend)

```
Scrapy Crawler (Instagram API) → Supabase (Cloud DB) → NLP/Mineradores (Workers Locais) → Motor de Relatórios (FPDF2)
                                                                               ↓
                                                                  Dashboard Frontend (UI/UX)
```

---

## 🚀 Instalação e Configuração

### 1. Requisitos do Sistema
- Python 3.10+
- Conta Supabase (Banco de Dados Cloud)
- Conta ativa no Instagram (Para extração do cookie `sessionid`)
- *(Opcional)* Groq Cloud API (Para futura classificação de IA)

### 2. Preparar Ambiente
```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```

### 3. Configurar Credenciais (.env)
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOi...
INSTAGRAM_SESSIONID=your_session_id_here
# GROQ_API_KEY=gsk_... (Para o módulo de IA)
```

---

## 🎯 Funcilidades Implementadas

✅ **Coleta Resiliente via Scrapy**: Extração nativa da API REST do Instagram, independente de terceiros (RapidAPI), com tratamento de paginação.
✅ **Banlco de Dados Idempotente**: Inserção à prova de falhas e duplicatas usando UPERTS no Supabase.
✅ **Motor PASA NLP**: Lematização avançada com spaCy, preservação de negações e tratamento forense de emojis.
✅ **Análise Temporal e Clustering**: Detecção de anomalias (picos de agressividade) e agrupamento semântico via KMeans.
✅ **Dossiê PDF (UTF-8)**: Geração de relatórios nativos em português sem bugs de codificação.

---

## ⚖️ Governança e Ética

1. Ferramenta desenvolvida em conformidade com as diretrizes do **TSE 2026** sobre rotulagem de IA.
2. Focada em transparência democrática e proteção da integridade pública.
3. A base de dados captura *comentários públicos* de figuras políticas monitoradas.

> **Aviso Legal**: O sistema Sentinela é uma plataforma independente. Os dados processados são de domínio público digital.
