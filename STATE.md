# 📊 STATE.md - Sentinela Democrática

**Última Atualização:** 2026-05-15
**Versão Core:** PASA v44.0
**Status do Sistema:** Operação Contínua e Autônoma

## 1. Estado Atual do Ecossistema
O Sentinela Democrática opera como um sistema distribuído de inteligência de dados, focado na análise informacional de discurso político em redes sociais. O scraping e o processamento de IA ocorrem em um Nó Local protegido, enquanto a visualização e consumo de dados ocorrem em uma interface web online.

## 2. Componentes Principais (v44)

### Nó Local (Master Server)
- **Orquestrador:** `local_server.py` (Execução Serial, Fila Inteligente, Cooldown de 6h).
- **Guardião:** `watchdog.py` (Auto-cura, reinício em caso de crash, alertas WhatsApp via CallMeBot).
- **Interface:** War Room (Terminal CLI com log de operações em tempo real).
- **Sincronização:** Git Push automático de JSONs de perfil de ameaças para o frontend online.

### Motor de Inteligência
- **Classificador Primário:** Gemini 1.5 Flash (Integrado com o MCA v2.2 e Framework CCF).
- **Auditor Cruzado:** Groq (Llama 3) para verificação anti-alucinação de amostras de alta confiança.
- **Análise de Deriva:** Monitoramento contínuo da distribuição de categorias para detecção de viés.
- **Metodologia:** MSAL (Metodologia Sentinela de Análise Léxica).

### Infraestrutura de Dados (Supabase)
- **Fonte da Verdade:** Tabela `comentarios` com métricas CCF (`ccf_density`, `ccf_sync`, `ccf_performativity`).
- **Fila de Coleta:** `fila_coleta` com controle de status e cooldown temporal.
- **Gamificação:** `worker_ledger` registrando XP e Níveis dos agentes.

## 3. Proteções Jurídicas e Acadêmicas Ativas
- O sistema produz **Indícios e Informações de Risco**, NÃO produz laudos, provas ou análises forenses.
- A metodologia operacional é denominada **MSAL**, desvinculando nomes de pesquisadores do fluxo de processamento.
- As referências acadêmicas (ex: Vichi, UFSCar) estão isoladas na seção de referências do MCA v2.2.
