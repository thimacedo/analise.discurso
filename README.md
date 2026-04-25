# 🔬 ForenseNet - Análise de Discurso de Ódio em Campanhas Políticas

Pipeline completo para coleta, análise e visualização de discurso de ódio em comentários do Instagram, baseado na metodologia do professor Leonardo Vichi de Linguística Forense Digital.

---

## 📋 Arquitetura

```
Instagram Graph API → Coletor → Corpus Builder → Pré-processamento NLP → Classificador IA → Análise Estatística → Visualizações → Relatório Pericial
```

---

## 🚀 Instalação e Configuração

### 1. Requisitos do Sistema
- Python 3.10+
- Acesso a conta Instagram (para coleta de dados)
- Chave API Anthropic Claude (opcional, para classificação contextual)

### 2. Preparar Ambiente

```bash
# 1. Criar ambiente virtual
python -m venv forense_env

# 2. Ativar ambiente virtual
# Windows:
forense_env\Scripts\activate

# Linux/Mac:
source forense_env/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Baixar modelo NLP português
python -m spacy download pt_core_news_lg
```

### 3. Configurar Credenciais

Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais:
```bash
INSTAGRAM_USERNAME=seu_usuario
INSTAGRAM_PASSWORD=sua_senha
ANTHROPIC_API_KEY=sua_chave_api (opcional)
```

---

## ▶️ Executar Análise

Edite o arquivo `main_pipeline.py` e adicione os nomes de usuário dos candidatos que deseja monitorar:

```python
CANDIDATES = [
    "usuario_candidato_1",
    "usuario_candidato_2",
    "usuario_candidato_3"
]
```

Execute o pipeline completo:
```bash
python main_pipeline.py
```

---

## 📁 Arquivos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `dados_brutos.csv` | Dados originais coletados do Instagram |
| `corpus_processado.csv` | Corpus após limpeza e tokenização |
| `corpus_classificado.csv` | Resultados completos da classificação |
| `frequencias_terminos.csv` | Termos mais frequentes no corpus |
| `relatorio_pericial.html` | Relatório final completo com análises |
| `nuvem_geral.png` | Nuvem de palavras geral |
| `nuvem_[categoria].png` | Nuvens por categoria de ódio |
| `categories.png` | Distribuição por categorias |
| `top_terms.png` | Termos mais frequentes |
| `timeline.png` | Evolução temporal do discurso de ódio |

---

## 🎯 Funcionalidades

✅ **Coleta Automática**: Extrai comentários de múltiplos posts de políticos
✅ **Pré-processamento NLP**: Limpeza, normalização, tokenização e lematização
✅ **Classificação Híbrida**: Combina palavras-chave + IA contextual
✅ **Análise Temporal**: Detecta picos de discurso de ódio
✅ **Análise de Usuários**: Identifica perfis com comportamento hostil recorrente
✅ **Agrupamento Temático**: Clustering de comentários por tema
✅ **Visualizações Profissionais**: Gráficos e nuvens de palavras
✅ **Relatório Automático**: Geração de relatório pericial em HTML

---

## 🔍 Categorias de Discurso de Ódio

| Categoria | Nível de Severidade |
|-----------|----------------------|
| Transfobia | 9/10 |
| Racismo | 8/10 |
| Homofobia | 7/10 |
| Xenofobia | 7/10 |
| Misoginia | 6/10 |

---

## ⚖️ Considerações Legais

1. Esta ferramenta respeita a **LGPD** e os Termos de Serviço do Instagram
2. Dados coletados são para fins acadêmicos e de pesquisa
3. A classificação automática **deve ser validada por análise humana** para casos ambíguos
4. Não utilize para vigilância massiva ou sem consentimento adequado

---

## 📚 Metodologia

Este projeto implementa a metodologia desenvolvida pelo **Prof. Leonardo Vichi** que combina:
- Linguística Forense
- Processamento de Linguagem Natural
- Mineração de Dados
- Inteligência Artificial
- Direito Digital

---

## 🛠️ Estrutura do Código

| Arquivo | Função |
|---------|--------|
| `instagram_collector.py` | Módulo de coleta de dados do Instagram |
| `corpus_builder.py` | Pré-processamento e construção do corpus |
| `hate_classifier.py` | Classificação de discurso de ódio |
| `data_mining.py` | Análise estatística e mineração de dados |
| `visualizer.py` | Geração de gráficos e relatórios |
| `main_pipeline.py` | Pipeline principal de execução |

---

> **Aviso**: Esta ferramenta é destinada exclusivamente para fins acadêmicos, de pesquisa e para promoção de ambientes digitais mais seguros e respeitosos.
