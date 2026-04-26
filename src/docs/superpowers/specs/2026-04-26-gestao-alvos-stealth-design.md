# Design Spec: Gestão de Alvos Sentinela (v15.5.0)

**Data:** 2026-04-26
**Status:** Aprovado
**URL:** `/addalvo`

## 1. Objetivo
Desacoplar a gestão de alvos de monitoramento do perfil do Instagram `@monitoramento.discurso`, centralizando o controle em uma interface administrativa protegida e resiliente a bloqueios.

## 2. Arquitetura de Segurança
- **Mecanismo:** TOTP (Time-based One-Time Password) via Google Authenticator.
- **Segredo:** Armazenado no `.env` como `SENTINELA_ADMIN_TOTP_SECRET`.
- **Fluxo:** 
  1. Usuário acessa `/addalvo`.
  2. Tela de bloqueio solicita código de 6 dígitos.
  3. API valida via `pyotp`.
  4. Token de sessão temporário emitido para o frontend (LocalStorage).

## 3. Componentes da Interface (`/addalvo`)
- **Header:** Resumo de status (Alvos ativos/inativos) e botão de Logout (limpa sessão).
- **Módulo Inclusão Única:** 
  - Campos: `@username`, `Nome Completo`, `Cargo`, `UF`.
  - Validação: Remoção automática de espaços e "@".
- **Módulo Importação Lote:**
  - Dropzone para arquivos `.csv`.
  - Botão "Baixar Modelo CSV" (colunas: `username,full_name,cargo,estado`).
- **Módulo Gestão de Alvos:**
  - Campo de busca em tempo real.
  - Tabela com paginação exibindo perfis.
  - Botão Toggle (Ativo/Inativo) para cada perfil.

## 4. Endpoints da API (FastAPI)
- `POST /api/v1/admin/auth/verify`: Valida o código TOTP.
- `GET /api/v1/admin/targets`: Lista todos os alvos com filtros.
- `POST /api/v1/admin/targets/upsert`: Adiciona ou atualiza um alvo único.
- `POST /api/v1/admin/targets/import`: Processa arquivo CSV.
- `PATCH /api/v1/admin/targets/{username}/status`: Altera o status de monitoramento.
- `GET /api/v1/admin/targets/template`: Retorna o arquivo CSV modelo.

## 5. Mudanças no Banco de Dados (Supabase)
- Utilização da tabela `candidatos` existente.
- Certificar que as colunas `username` (unique), `nome_completo`, `cargo`, `estado` e `status_monitoramento` estão presentes.

## 6. Plano de Testes
- [ ] Validar geração e aceitação do código TOTP.
- [ ] Testar importação de CSV com 100+ linhas.
- [ ] Verificar se o Toggle de status reflete imediatamente na lista de alvos do banco.
