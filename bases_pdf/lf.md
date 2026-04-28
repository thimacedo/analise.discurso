Para converter os ficheiros fornecidos num formato compatível com o Gemini CLI (ou para leitura direta num bloco Markdown estruturado), pode utilizar o seguinte conteúdo. Este documento consolida o código-fonte, as instruções de instalação e os metadados do projeto.



# Linguística Forense UFRN - Extração de Termos e N-Gramas

Este repositório contém ferramentas desenvolvidas para a disciplina Linguística Forense e Tecnologias Digitais da Pós-Graduação em Linguística Forense da Universidade Federal do Rio Grande do Norte. O objetivo é permitir a extração automatizada de frequências lexicais e sequências de palavras (n-gramas) para análise forense.

## 1. Configuração do Ambiente

### Dependências (`requirements.txt`)
```text
spacy=3.7.0
matplotlib=3.8.0
wordcloud=1.9.3
```


### Comandos de Instalação
```bash
# Instalação do Python (UbuntuDebian)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Criação e ativação do ambiente virtual
python3 -m venv .venv
source .venvbinactivate

# Instalação de bibliotecas e modelo de linguagem
pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```


---

## 2. Scripts de Processamento

### Script `app_words.py`
Gera nuvens de palavras e listas de frequência para verbos, substantivos e adjetivos.

```python
# Autor Leonardo Perin Vichi
# Data 11.04.2026

from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Dict
import csv
import matplotlib.pyplot as plt
import spacy
from wordcloud import WordCloud

# Configurações
INPUT_FILE = texto.txt
TOP_N = 30
MODEL_NAME = pt_core_news_lg
MIN_WORD_LENGTH = 2
USE_LEMMA = True
SAVE_IMAGES = True
SHOW_IMAGES = True
SAVE_CSV = True

def load_text(file_path str) - str
    path = Path(file_path)
    if not path.exists()
        raise FileNotFoundError(fArquivo não encontrado {path.resolve()})
    text = path.read_text(encoding=utf-8).strip()
    if not text
        raise ValueError(O arquivo está vazio.)
    return text

def normalize_token(token) - str  None
    if token.is_stop or token.is_punct or token.is_space or token.like_num
        return None
    if token.pos_ not in {VERB, NOUN, ADJ}
        return None
    base = token.lemma_ if USE_LEMMA else token.text
    base = base.strip().lower()
    if not base or len(base)  MIN_WORD_LENGTH or base in {-pron-, —, -, _}
        return None
    if not any(ch.isalpha() for ch in base)
        return None
    return base

def count_by_pos(doc) - Dict[str, Counter]
    counters = {VERB Counter(), NOUN Counter(), ADJ Counter()}
    for token in doc
        normalized = normalize_token(token)
        if normalized
            counters[token.pos_][normalized] += 1
    return counters

def create_wordcloud(frequencies Dict[str, int], title str, output_file str  None = None)
    if not frequencies return
    wc = WordCloud(width=1600, height=900, background_color=white, collocations=False).generate_from_frequencies(frequencies)
    plt.figure(figsize=(14, 8))
    plt.imshow(wc, interpolation=bilinear)
    plt.axis(off)
    plt.title(title, fontsize=18)
    if output_file plt.savefig(output_file, dpi=300, bbox_inches=tight)
    if SHOW_IMAGES plt.show()
    else plt.close()

def save_csv(filename str, freq_dict Dict[str, int], column_name str)
    with open(filename, w, encoding=utf-8, newline=) as f
        writer = csv.writer(f)
        writer.writerow([column_name, frequencia])
        for word, freq in freq_dict.items()
            writer.writerow([word, freq])

def main()
    try
        nlp = spacy.load(MODEL_NAME)
    except OSError
        print(fInstale o modelo python -m spacy download {MODEL_NAME})
        return
    text = load_text(INPUT_FILE)
    doc = nlp(text)
    counters = count_by_pos(doc)
    
    data = [
        (dict(counters[VERB].most_common(TOP_N)), verbos),
        (dict(counters[NOUN].most_common(TOP_N)), substantivos),
        (dict(counters[ADJ].most_common(TOP_N)), adjetivos)
    ]

    for top_items, label in data
        if SAVE_IMAGES create_wordcloud(top_items, f30 {label} mais frequentes, fnuvem_{label}.png)
        if SAVE_CSV save_csv(f{label}.csv, top_items, label[-1])

if __name__ == __main__
    main()
```


### Script `app_grams.py`
Extrai bigramas e trigramas sem cruzar as fronteiras das sentenças.

```python
# Autor Leonardo Perin Vichi
# Data 11.04.2026

from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple
import csv
import matplotlib.pyplot as plt
import spacy
from wordcloud import WordCloud

INPUT_FILE = texto.txt
TOP_N = 30
MODEL_NAME = pt_core_news_lg
LOWERCASE = True
REMOVE_NUMBERS = True
SAVE_IMAGES = True
SAVE_CSV = True

def normalize_token(token) - str  None
    if token.is_space or token.is_punct return None
    if REMOVE_NUMBERS and token.like_num return None
    value = token.text.strip().lower() if LOWERCASE else token.text.strip()
    return value if value else None

def extract_sentence_sequences(doc) - List[List[str]]
    sentences = []
    for sent in doc.sents
        tokens = [normalize_token(t) for t in sent if normalize_token(t)]
        if tokens sentences.append(tokens)
    return sentences

def count_ngrams(sentences List[List[str]], n int) - Counter
    counter = Counter()
    for sent in sentences
        ngrams = [tuple(sent[ii+n]) for i in range(len(sent)-n+1)]
        counter.update(ngrams)
    return counter

def main()
    nlp = spacy.load(MODEL_NAME)
    text = Path(INPUT_FILE).read_text(encoding=utf-8)
    doc = nlp(text)
    sentences = extract_sentence_sequences(doc)
    
    for n, label in [(2, bigramas), (3, trigramas)]
        counts = count_ngrams(sentences, n)
        top = { .join(k) v for k, v in counts.most_common(TOP_N)}
        if SAVE_CSV
            with open(f{label}.csv, w, encoding=utf-8, newline=) as f
                writer = csv.writer(f)
                writer.writerow([label, frequencia])
                for k, v in top.items() writer.writerow([k, v])

if __name__ == __main__
    main()
```


---

## 3. Licença e Uso
O software é disponibilizado sob a Licença MIT. É fornecido como está, sem garantias de qualquer tipo por parte dos autores ou detentores dos direitos de autor (Leonardo Vichi, 2026).