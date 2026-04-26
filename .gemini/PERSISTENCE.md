# 🛡️ PROTOCOLO DE PERSISTÊNCIA - SENTINELA

## 🚫 PROIBIDO DESFAZER (PONTOS PACIFICADOS)
1. **Navegação SPA**: Links internos DEVEM ser `#monitor`, `#dossie`, `#map`. Nunca use caminhos relativos para navegação entre abas.
2. **Título do Site**: Deve ser apenas `SENTINELA`. Proibido ícones (favicon) ou letras gregas/emojis.
3. **Mídia**: As imagens de perfil DEVEM usar o atributo `onerror` para fallback de iniciais.
4. **Independência**: Nenhuma menção a UFRN ou nomes externos. Metodologia é PASA (Sentinela).

## 📁 ESTRUTURA DE ARQUIVOS
- A raiz deve conter `index.html` e `addalvo.html`.
- O diretório `src/` e `docs/` devem estar na raiz para acesso direto do Vercel.

## 📡 REGRAS DE API
- Toda rota `/api/v1/` deve retornar JSON.
- O backend (`api/index.py`) NÃO deve servir HTML; o Vercel cuida do roteamento estático.
