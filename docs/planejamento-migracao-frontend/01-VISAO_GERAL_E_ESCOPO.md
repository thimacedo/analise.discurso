# Planejamento de Migração - Visão Geral e Escopo

## 🎯 Objetivo
Migrar o atual frontend do projeto Sentinela Democrática (atualmente baseado em Vanilla JS, manipulação direta de DOM e Tailwind CSS via CDN) para uma arquitetura moderna e escalável baseada no protótipo fornecido (`PROPOSTA.MD`).

## 📦 Escopo da Migração
A proposta baseia-se num stack de ponta (Bleeding Edge):
- **Framework:** Next.js 16 (App Router) com React 19.
- **Estilização:** Tailwind CSS v4 e Shadcn UI (Radix UI) para componentes acessíveis e modulares.
- **Gráficos e KPIs:** Recharts (substituindo renderizações manuais ou bibliotecas legadas).
- **Gerenciamento de Estado:** Zustand e TanStack React Query para cacheamento de servidor.
- **Ícones:** Lucide React.
- **Ferramental:** Bun como gerenciador de pacotes/runtime (opcional, npm/uv na infraestrutura atual).

## 🚀 Motivação (Por que migrar?)
1. **Manutenibilidade:** O atual `app.js` e `ui.js` concentram muita responsabilidade de manipulação do DOM. Com o React, a interface será declarativa e orientada a componentes.
2. **Design System:** O uso do Shadcn UI garante uma interface com nível profissional, padronizada e polida ("War Room" estética).
3. **Performance:** O Next.js (App Router) permite renderização do lado do servidor (SSR), o que tira carga do cliente e melhora o tempo de carregamento de grandes volumes de dados (comentários de ódio).
4. **Alinhamento ao PRD:** Um frontend mais robusto complementa o backend aprimorado para a ingestão massiva de dados, suportando painéis analíticos complexos sem gargalos no navegador.