---
name: qwen-local-coder
description: Assistência de programação local de alta performance via Qwen Local Hub. Use para tarefas de codificação que exigem latência zero, privacidade total ou processamento intensivo de lógica.
---

# Qwen Local Coder

Esta skill habilita o uso do modelo **Qwen** rodando localmente no seu hardware para acelerar o ciclo de desenvolvimento.

## Quando usar

1. **Latência Zero**: Para refatorações rápidas onde a latência da nuvem é um impedimento.
2. **Privacidade Total**: Processamento de arquivos sensíveis que não devem sair do ambiente local.
3. **Lógica Complexa**: Quando o motor PASA ou outros modelos de nuvem atingem limites de cota.

## Como funciona

A skill utiliza o script `scripts/query_qwen.py` para se comunicar com um servidor compatível com a API do OpenAI (ex: Ollama, LM Studio, vLLM) rodando no seu computador.

### Configuração (via .env)

```bash
QWEN_ENDPOINT=http://localhost:11434/v1/chat/completions # Exemplo Ollama
QWEN_MODEL=qwen2.5-coder:7b
```

## Workflows

### 1. Refatoração de Código
Delegue a limpeza de funções extensas para o Qwen:
`py .gemini/skills/qwen-local-coder/scripts/query_qwen.py "Refatore esta função para seguir SOLID: [codigo]"`

### 2. Auditoria de Segurança
Identifique vulnerabilidades em tempo real sem expor o código à nuvem.
