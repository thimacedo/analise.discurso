# Dossiês de Inteligência PDF (Sentinela Democrática) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar a geração e exportação de Dossiês de Inteligência em formato PDF, consolidando dados de clima, redes coordenadas e alertas em um documento profissional e visualmente estruturado.

**Architecture:** A geração de PDF será centralizada em um novo serviço especializado (`DossieService`), utilizando a biblioteca `fpdf2` (evolução do fpdf atual para melhor suporte a Unicode/UTF-8). O serviço consumirá dados do banco (Supabase) e integrará com o motor de N-Gramas já existente.

**Tech Stack:** Python 3.x, `fpdf2` (substituindo `fpdf`), `httpx`, `Supabase SDK`.

---

### Task 1: Setup de Dependências e Estrutura de Pastas

**Files:**
- Modify: `requirements.txt`
- Create: `data/reports/.gitkeep`

- [ ] **Step 1: Atualizar dependências**
Substituir `fpdf` por `fpdf2` para garantir suporte total a Unicode (acentuação) e recursos modernos de layout.

```text
# Adicionar ao requirements.txt
fpdf2>=2.7.0
```

- [ ] **Step 2: Instalar dependências**
Run: `pip install fpdf2`

- [ ] **Step 3: Garantir diretório de saída**
Criar a pasta onde os dossiês serão armazenados localmente antes da disponibilização.
Run: `mkdir -p data/reports`

- [ ] **Step 4: Commit**
```bash
git add requirements.txt
git commit -m "chore: add fpdf2 dependency and setup reports directory"
```

---

### Task 2: Refatoração do Motor de PDF (DossieService)

**Files:**
- Create: `processing/dossie_service.py`
- Modify: `processing/report_generator.py` (marcar como legado ou remover)

- [ ] **Step 1: Criar a classe base do Dossiê**
Implementar o `DossieService` herdando de `FPDF` com suporte a fontes Unicode.

```python
from fpdf import FPDF
from datetime import datetime

class DossieService(FPDF):
    def header(self):
        # Logo ou Identificador do Sentinela
        self.set_font("helvetica", "B", 15)
        self.set_text_color(37, 99, 235) # Azul Sentinela
        self.cell(0, 10, "SENTINELA DEMOCRÁTICA", ln=1, align="L")
        self.set_font("helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Dossiê de Inteligência e Análise Situacional", ln=1, align="L")
        self.line(10, 27, 200, 27)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()} | Fundamento Técnico - Uso Informativo", align="C")

    def add_section_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, ln=1, fill=True)
        self.ln(5)
```

- [ ] **Step 2: Implementar lógica de conteúdo (Insights e Alertas)**
Adicionar métodos para renderizar os blocos de dados sanitizados.

```python
    def render_insight(self, item):
        self.set_font("helvetica", "B", 10)
        self.set_text_color(0, 0, 0)
        ctx = item.get('candidatos', {}).get('username', 'Monitorado')
        self.cell(0, 8, f"ALERTA: {ctx}", ln=1)
        
        self.set_font("helvetica", "", 9)
        self.multi_cell(0, 5, f"Conteúdo Identificado: {item.get('texto_bruto', '')}")
        
        status = "AGRESSIVO" if item.get('is_hate') else "NEUTRO"
        color = (220, 38, 38) if item.get('is_hate') else (37, 99, 235)
        self.set_text_color(*color)
        self.set_font("helvetica", "B", 9)
        self.cell(0, 8, f"Status: {status} | Categoria: {item.get('categoria_ia', 'N/A')}", ln=1)
        self.ln(4)
```

- [ ] **Step 3: Testar geração básica**
Criar um script de teste `tests/test_pdf_generation.py`.

- [ ] **Step 4: Commit**
```bash
git add processing/dossie_service.py
git commit -m "feat: implement professional DossieService using fpdf2"
```

---

### Task 3: Integração com Dados Reais (N-Gramas e Redes)

**Files:**
- Modify: `processing/dossie_service.py`
- Modify: `core/main.py` (Exportar função de análise para o PDF)

- [ ] **Step 1: Adicionar seção de Redes Coordenadas**
Implementar a visualização textual dos padrões de repetição linguística.

- [ ] **Step 2: Criar endpoint/script de trigger**
Vincular o botão "Exportar Inteligência" da UI (via API se necessário) ao serviço de geração.

- [ ] **Step 3: Validar contra Glossário do TSE**
Garantir que os termos automáticos não usem terminologia forense proibida (ex: mudar "Evidência" para "Fundamento Técnico").

- [ ] **Step 4: Commit**
```bash
git commit -m "feat: integrate n-gram analysis into Dossie PDF"
```
