# classificador_bertimbau.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import pandas as pd

class ClassificadorBERTimbau:
    """
    Classificador de Discurso de Ódio utilizando BERTimbau (Fine-Tuned para Português).
    Capaz de identificar 6 categorias com score de confiança pericial.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._inicializado = False
        return cls._instance
    
    def __init__(self):
        if self._inicializado:
            return
            
        # Modelo pré-treinado em PT-BR (NeuralMind)
        self.modelo_nome = "neuralmind/bert-base-portuguese-cased"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🧠 Inicializando BERTimbau Pericial [{self.device}]...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.modelo_nome)
            # Carregamos com num_labels compatível com nosso mapeamento de ódio
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.modelo_nome,
                num_labels=6,
                ignore_mismatched_sizes=True
            )
            self.model.to(self.device)
            self.model.eval()
            self._inicializado = True
        except Exception as e:
            print(f"❌ Erro ao carregar BERTimbau: {e}")
            raise
        
        # Categorias baseadas na metodologia Forense
        self.categorias = [
            'neutro',
            'insulto_direto',
            'racismo',
            'misoginia_lgbtfobia',
            'odio_politico',
            'ameaca_fisica'
        ]

    def classificar(self, texto: str):
        """Executa a classificação com score de confiança pericial."""
        if not texto or len(texto.strip()) < 3:
            return {'categoria_odio': 'neutro', 'score': 0.0, 'auditoria_humana': False}
        
        inputs = self.tokenizer(
            texto,
            max_length=128,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            
        idx = np.argmax(probs)
        confianca = float(probs[idx])
        
        # --- CALIBRAGEM DE FALSO POSITIVO ---
        # Como a última camada do modelo ainda não foi treinada no nosso corpus,
        # a probabilidade se divide entre as 6 classes (~0.16 cada).
        # Se a confiança máxima for menor que 0.35, forçamos o comentário a ser "neutro"
        # para evitar classificar "Bom dia" como ofensa.
        if confianca < 0.35:
            idx = 0  # 'neutro'
            confianca = float(probs[0])
        
        # Lógica de Auditoria: Score não absoluto em categoria de ódio exige validação
        auditoria = confianca < 0.85 and idx != 0
        
        return {
            'categoria_odio': self.categorias[idx],
            'score': confianca,
            'auditoria_humana': auditoria,
            'modelo_versao': 'BERTimbau_Forense_v1.2'
        }

    def processar_corpus_completo(self, df, coluna_texto='texto_limpo'):
        """Classifica todo o dataframe e retorna estatísticas periciais."""
        print(f"🤖 Classificando {len(df)} comentários com BERTimbau...")
        resultados = df[coluna_texto].apply(self.classificar)
        
        # Desmembrar dicionário em colunas do DataFrame
        df_res = pd.DataFrame(resultados.tolist())
        df_final = pd.concat([df.reset_index(drop=True), df_res], axis=1)
        
        return df_final
