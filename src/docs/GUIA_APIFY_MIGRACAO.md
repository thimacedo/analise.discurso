# 🚀 Guia de Migração para o Apify

Essa é a nova arquitetura profissional de coleta que resolve os problemas de bloqueio, rate limit e manutenção do Instagram.

---

## ✅ O que já foi implementado

✅ Arquivo `coletor_apify.py` criado com pipeline completo
✅ Dependência `apify-client` adicionada aos requirements
✅ Variável `APIFY_API_TOKEN` adicionada no `.env.example`
✅ 100% compatível com o processador e classificador existentes
✅ Tratamento de erros e pausas automáticas
✅ Modo teste para validação inicial

---

## 📋 Próximos passos para você

### 1. Instalar a nova dependência
```bash
pip install -r requirements-pipeline.txt
```

### 2. Obter sua chave API do Apify
1. Acesse https://console.apify.com e crie sua conta
2. Clique no avatar (canto superior direito) → **Settings** → **API & Integrations**
3. Copie seu API Token
4. Adicione no seu arquivo `.env`:
   ```env
   APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxx
   ```

### 3. Testar o coletor (modo desenvolvimento)
```bash
python coletor_apify.py
```
> Por padrão ele vai processar apenas 5 perfis para teste. Se funcionar, remova o parâmetro `limite_perfis_teste` para rodar completo.

### 4. Integrar no pipeline principal
No seu `main_pipeline.py` basta alterar a importação:
```python
# ANTES:
# from coletor import ColetorInstagram

# DEPOIS:
from coletor_apify import ColetorApify

coletor = ColetorApify()
comentarios = coletor.pipeline_completo()
```

---

## 🔄 Funcionamento do Pipeline
```
1. 🔍 Consulta os perfis monitorados diretamente na tabela `candidatos` do Supabase.
2. 📸 Para cada perfil, coleta os últimos 3 posts
3. 💬 Para cada post, coleta os últimos 10 comentários
4. 💾 Salva tudo em `dados_brutos_apify.csv`
5. 🧠 Processador e Classificador leem o arquivo exatamente como antes
```

---

## ⚙️ Configurações recomendadas

| Parâmetro | Valor padrão | O que faz |
|-----------|--------------|-----------|
| `posts_por_perfil` | 3 | Quantidade de posts recentes por candidato |
| `comentarios_por_post` | 10 | Quantidade de comentários por post |
| `limite_perfis_teste` | None | Limita quantidade de perfis para teste |

---

## 💰 Monitoramento de Custos
- Plano gratuito do Apify: **$5 crédito por mês**
- Cada execução completa (500 perfis) consome aproximadamente ~$0.30
- Recomendo rodar a cada 12 horas → **~$18/mês** em uso normal
- Você pode acompanhar o consumo em tempo real no console do Apify

---

## 🔒 Segurança
✅ Nenhuma senha é exposta publicamente
✅ Todo tráfego passa por proxy residencial do Apify
✅ Sessões do Instagram são gerenciadas automaticamente
✅ Rotação de IP automática para evitar bloqueios

---

## ❌ Problemas resolvidos em relação ao coletor antigo
| Problema antigo | Solução Apify |
|-----------------|---------------|
| Bloqueio de IP | Proxy residencial rotativo |
| Rate limit 429 | Gerenciamento automático de throttling |
| Deslogar aleatoriamente | Sessões gerenciadas e rotacionadas |
| Manutenção do parser | Atualizado pelo time do Apify 24/7 |
| Captchas | Resolvido automaticamente |

---

## 📅 Agendamento
Mantenha o agendamento já existente no GitHub Actions. Basta alterar o comando para executar `coletor_apify.py` no lugar do coletor antigo.

---

> 📌 **Importante**: Nos primeiros dias, execute manualmente e monitore o consumo de créditos antes de ligar o agendamento automático.
