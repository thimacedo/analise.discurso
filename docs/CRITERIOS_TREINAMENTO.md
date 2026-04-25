# Baliza de Treinamento: Linguística Forense e Discurso de Ódio
**Versão:** 1.0 (Baseada em Normas Jurídicas e Pesquisa Acadêmica Brasileira)
**Objetivo:** Estabelecer critérios objetivos para a classificação de mensagens e treinamento de modelos IA (BERTimbau/Qwen) no ecossistema ForenseNet.

---

## ⚖️ 1. Matriz de Critérios Jurídico-Periciais
Baseada nas diretrizes do **MPF**, **STF** e doutrina penal brasileira.

### A. Discurso de Ódio Penalmente Punível
Para ser classificado como ódio real (Flag Vermelha), o conteúdo deve apresentar:
1. **monitorado Protegido:** Ataque baseado em raça, cor, etnia, religião, procedência nacional, orientação sexual ou identidade de gênero.
2. **Desumanização:** Uso de termos que comparam seres humanos a animais, pragas ou objetos.
3. **Incitação:** Estímulo direto ou indireto à violência física ou exclusão social.
4. **Hostilidade Política Extrema:** Ataques que visam anular a dignidade do opositor, indo além da crítica à gestão (Injúria, Calúnia ou Difamação).

### B. Zona de Sombra (Falsos Positivos)
Não devem ser marcados como ódio (exceto se houver agressão explícita):
- **Crítica Institucional:** "Este governo é corrupto" ou "Este político é incompetente" (Lógica: Direito à crítica política).
- **Ironia e Sarcasmo:** Uso de figuras de linguagem sem incitação à violência.
- **Linguagem Informal de Apoio:** Uso de termos fortes ("Matou a pau", "Acabou com eles") em contextos de vitória ou debate.

---

## 🎓 2. Critérios Linguísticos e Acadêmicos (USP/UNICAMP/FGV)
Critérios para ajuste fino dos pesos da IA:

- **Intencionalidade (Mens rea):** A IA deve buscar marcadores de *animus injuriandi* (intenção de ofender).
- **Contextualidade:** Verificação do post original. Se o post é sobre "Causa Animal", a palavra "matar" no comentário deve ser analisada como denúncia, não como ódio.
- **Toxicidade Colaborativa:** Identificação de padrões de repetição (ataques coordenados por bots).

---

## 🛠️ 3. Taxonomia de Classificação (Labels)
| Categoria | Descrição | Flag |
| :--- | :--- | :--- |
| **ÓDIO_RACIAL** | Ataque direto a etnia ou cor. | 🚩 CRÍTICO |
| **ÓDIO_GENERO** | Misoginia, homofobia ou transfobia. | 🚩 CRÍTICO |
| **AMEAÇA_FISICA** | Promessa de dano à integridade. | 🚩 CRÍTICO |
| **INSULTO_POLITICO** | Xingamentos diretos sem base em pauta. | 🟠 ALERTA |
| **CRÍTICA_DURA** | Crítica severa mas dentro da lei. | ⚪ NEUTRO |
| **APOIO/EMOJI** | Emojis, elogios e incentivos. | ✅ SEGURO |

---

## 🔄 4. Gatilhos de Atualização (Continuous Learning)
Para manter nossos parâmetros sempre atualizados, o sistema deve disparar reavaliações quando:

1. **Mudança Legislativa:** Atualização no Código Penal (Ex: Inclusão de novos grupos protegidos).
2. **Drift de Linguagem:** Surgimento de novas gírias ou "dog whistles" (códigos usados por grupos de ódio para burlar filtros).
3. **Feedback do Perito:** Toda vez que você (Investigador) marcar um "Falso Positivo" no Dashboard, este `.md` deve ser consultado para ajustar o `cloud_classifier.py`.
4. **Novas Teses:** Inclusão de referências de repositórios (UFRN, UFU, UFMS) a cada 6 meses.

---

## 📚 Referências Consolidadas
- **Jurídico:** JOTA (Critérios de Caracterização), MPF (Respeite a Diferença).
- **Plataformas:** Meta (Hateful Conduct Policy).
- **Acadêmico:** Estudos USP (IA Transparente), Unicamp (Datasets de Ódio), FGV (Monitoramento de Redes).

---
**Próxima Revisão Agendada:** 18/10/2026
