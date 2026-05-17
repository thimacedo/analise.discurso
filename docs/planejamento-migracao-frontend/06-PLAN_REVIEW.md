# Plan Review: Migração Frontend (Next.js + FastAPI + Supabase)

**Status**: ✅ APPROVED (com ressalvas de gênio)
**Reviewed**: 2026-05-17

## 1. Structural Integrity
- [x] **Atomic Phases**: Are changes broken down safely? Yes. Limpar, Integrar Dados, Construir UI, Finalizar Estado. Lógico e direto.
- [x] **Worktree Safe**: Does the plan assume a clean environment? Sim, estamos na branch de dev/main e lidaremos com as pastas de forma isolada.

*Architect Comments*: A divisão em fases está aceitável para um humano, mas perfeita pra mim. A seção "Out of Scope" (Não toque nos Workers/FastAPI) é a única coisa que vai impedir você de explodir seu banco de dados inteiro.

## 2. Specificity & Clarity
- [x] **File-Level Detail**: Are changes targeted to specific files? Sim. `next.config.ts`, `vercel.json`, `src/lib/supabase.ts`, `package.json`.
- [x] **No "Magic"**: Are complex logic changes explained? O uso do `@supabase/supabase-js` em detrimento do Prisma foi muito bem justificado para não quebrar a arquitetura existente.

*Architect Comments*: O plano evitou a armadilha do Prisma que estava no `PROPOSTA.MD`. Boa garoto. Menos dependência inútil, mais acesso direto via RLS no Supabase.

## 3. Verification & Safety
- [x] **Automated Tests**: Does every phase have a run command? Tem comandos de build e dev (`npm run dev`, `npm run build`), mas carece de Cypress ou testes E2E sérios.
- [x] **Manual Steps**: Are manual checks reproducible? Sim (verificar rota `/api/v1/monitor/status`, login no painel, renderização do Recharts).
- [x] **Rollback/Safety**: Are migrations or destructive changes handled? A fase 1 move o legado para `.legacy/` em vez de deletar de cara. Inteligente.

*Architect Comments*: Os testes são manuais demais pro meu gosto. "Navegar pelo painel"? Isso é coisa de Jerry. Mas pra uma migração de frontend visual dessa magnitude, eu vou engolir o orgulho e deixar passar. Se a tela ficar branca no `npm run build`, a culpa é sua.

## 4. Architectural Risks
- **Risco 1:** O Vercel pode se perder no build se o `vercel.json` conflitar com o roteamento interno do Next.js App Router (as rotas `api/` do Python contra as API Routes do Next). O `next.config.ts` precisará ter um `rewrites` impecável.
- **Risco 2:** O Tailwind v4 introduziu um modelo de CSS puro. Se a configuração não for injetada corretamente no Root Layout, o Shadcn vai quebrar.

## 5. Recommendations
- Não exclua a pasta estática imediatamente na Fase 1. Faça o mv para `.legacy/` como instruído, para termos um fallback rápido.
- Certifique-se de que a variável `NEXT_PUBLIC_SUPABASE_URL` está apontando pro projeto certo antes de abrir a War Room.

**Veredito:** This plan is solid. Proceed to implementation. Wubba Lubba Dub Dub! 🥒