# 🛡️ Sentinela Democrática — Inteligência Situacional v15.6

Pipeline profissional para coleta, análise e visualização de discurso de ódio e tendências políticas, baseado no **Protocolo PASA** (Proprietário).

---

## 📋 Arquitetura

```
API Coleta → Cérebro de Inteligência → Motor PASA v15.6 → Dashboard Stealth → Dossiê Analítico
```

---

## 🚀 Instalação e Configuração

### 1. Requisitos do Sistema
- Python 3.10+
- Conta Supabase (Banco de Dados Cloud)
- Groq Cloud API (Motor de Inferência Llama 3.3)

### 2. Preparar Ambiente

```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```

### 3. Configurar Credenciais

Configure o arquivo `.env` conforme o `.env.example`:
```bash
SUPABASE_URL=...
SUPABASE_KEY=...
GROQ_API_KEY=...
SENTINELA_ADMIN_TOTP_SECRET=...
```

---

## 🎯 Funcionalidades

✅ **Coleta Resiliente**: Extração de dados via RapidAPI (Independentemente da sessão local).
✅ **Motor PASA v15.6**: Protocolo avançado de Linguística Forense proprietário.
✅ **Dashboard Stealth**: Visualização de alta performance com design de centro de comando.
✅ **Matriz de Guerra**: Gráfico nativo de impacto vs hostilidade.
✅ **Geopolítica**: Mapa de risco situacional por estado (UF).

---

## ⚖️ Governança e Ética

1. Esta ferramenta opera em total conformidade com as diretrizes do **TSE 2026** sobre rotulagem de IA.
2. Focada em transparência democrática e proteção da integridade pública.
3. A classificação automatizada utiliza blindagem semântica contra falsos positivos.

---

> **Aviso**: O sistema Sentinela é uma plataforma independente de monitoramento e análise de dados para gestão estratégica de crises narrativas.
