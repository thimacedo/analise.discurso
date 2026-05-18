# Implementação de Autenticação TOTP (2h)

## Problema
A página administrativa `addalvo.html` estava acessível publicamente sem autenticação, expondo endpoints de gestão de alvos e auditoria de dados.

## Solução Implementada
Foi implementado um sistema hibrido de segurança:

1.  **Mecanismo TOTP (Google Authenticator):**
    - Utiliza a biblioteca `pyotp` no backend para validar códigos de 6 dígitos.
    - Baseia-se na variável de ambiente `SENTINELA_ADMIN_TOTP_SECRET`.

2.  **Sessão Temporária (2 Horas):**
    - Tokens de sessão baseados em HMAC-SHA256.
    - O token contém um timestamp de expiração (`exp = time + 7200s`).
    - Assinado com `SUPABASE_KEY` para garantir integridade.

3.  **Frontend (addalvo.html):**
    - Modal de bloqueio (`auth-modal`) persistente.
    - Interceptador de requisições (`apiFetch`) que detecta erro 401 e força novo login.
    - Persistência em `localStorage` do token (não da senha).

## Dependências
- `pyotp`: Adicionado em `api/requirements.txt`.

## Manutenção
Caso seja necessário resetar o segredo, altere `SENTINELA_ADMIN_TOTP_SECRET` e o usuário deverá re-escanear o QR Code gerado por `scripts/generate_totp_secret.py`.
