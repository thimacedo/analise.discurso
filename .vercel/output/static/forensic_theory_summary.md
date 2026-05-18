# Forensic Theory Summary: Sentinela Democrática
**Version:** 1.0.0 (Synthesis of PASA v16.4 & Vichi-Sentinela Methodology)
**Status:** Operational Reference for AI Classification Workers

## 1. Executive Summary
This document synthesizes the theoretical base for the Sentinela Democrática project, integrating forensic linguistic principles, the PASA v16.4 taxonomy, and the Vichi-Sentinela methodology for coordinated attack detection.

## 2. Forensic Linguistic Rules (Vichi Method)
Based on the **Vichi-Sentinela Methodology**, all text processing must follow these immutable rules to ensure evidentiary integrity:

### 2.1. Norm-V (Normalization)
- **POS Filtering**: Priority extraction of **VERB**, **NOUN**, and **ADJ**. Adjectives are the primary carriers of offensive load.
- **Lemmatization**: Grouping lexical variations (e.g., "matar", "matando", "matou" -> "matar") to identify underlying intent.
- **Sentence Boundary**: Extraction of n-grams must **NOT** cross punctuation boundaries to preserve syntactic cohesion.

### 2.2. Lexical Signatures (N-Grams)
- **Bigrams (N=2)**: Targeted identification of targets and recurrent pejoratives (e.g., "político lixo").
- **Trigrams (N=3)**: Identification of slogans, coordination instructions, or specific threats (e.g., "vamos quebrar tudo").

## 3. Taxonomy of Hostility (PASA v16.4)
The system classifies threats according to the **Matriz Taxonômica de Ameaças Democráticas (MTAD)**:

| Category | Key Markers / Lexical Patterns | Risk Level |
| :--- | :--- | :--- |
| **Xenofobia Regional** | "pobre", "ingrato", "analfabeto", "miserável", "burro" (Target: Nordeste). | **CRITICAL** |
| **Racismo Religioso** | "macumba", "vodu", "encosto", "chuta que é macumba", "guerra espiritual". | **HIGH** |
| **Misoginia Política** | "vaca", "puta", "louca", "piranha", "vagabunda", "redpill". | **CRITICAL** |
| **Ataque Institucional** | "ditadura da toga", "fraude nas urnas", "Xandão", "comprado". | **ALTO** |
| **Rigor Criminal** | "ladrão", "corrupto", "chefe de quadrilha", "meliante" (without proof). | **CRITICAL** |
| **Ameaça Direta** | "tem que levar tiro", "paredão", "morte ao candidato". | **CRITICAL** |

## 4. Irony and Sarcasm Scanner
The system identifies **Semantic Dissonance** where positive words are used to convey contempt:

- **Dissonance Type A (Inverted Praise)**: "Grande democrata esse aí" (in a context of censorship).
- **Dissonance Type B (Hyperbolic Congratulations)**: "Parabéns pelo roubo".
- **Lexical Indicators**: Excessive emojis (🤡, 👏), tone indicators (#sarcasm), and specific keywords ("lol", "claro", "certeza").

## 5. 'Calculated Confidence' Theoretical Framework (CCF)
The **Calculated Confidence Framework** determines the reliability of an IA verdict based on three weighted layers:

### 5.1. Layer 1: Lexical Density (30%)
- **Marker Concentration**: The ratio of offensive adjectives/nouns to the total word count.
- **Threshold**: Density > 0.4 triggers higher confidence in "Hate Speech" detection.

### 5.2. Layer 2: Synchronization & Coordination (40%)
- **Density of Bigrams**: >5 identical bigrams between different profiles indicates coordinated bot activity (Astroturfing).
- **Temporal Sync**: Identical trigrams in windows < 300 seconds elevates the "Risk" score.

### 5.3. Layer 3: Semantic Performativity (30%)
- **Butler Principle**: Assessing the *action* performed by the speech (e.g., silencing, dehumanizing).
- **Calculated Veredict**: Confidence = (Density * 0.3) + (Sync * 0.4) + (Performativity * 0.3).

---
*Document synthesized by Pickle Rick (Morty Worker) on 2026-05-01.*
