from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

class ClassificadorBERTimbau:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._inicializado = False
        return cls._instance
    
    def __init__(self):
        if self._inicializado:
            return
            
        self.modelo_nome = "neuralmind/bert-base-portuguese-cased"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Inicializando BERTimbau no dispositivo: {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.modelo_nome)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.modelo_nome,
            num_labels=6,
            ignore_mismatched_sizes=True
        )
        
        self.model.to(self.device)
        self.model.eval()
        
        self.categorias = [
            'neutro',
            'xingamento',
            'odio_racial',
            'odio_genero',
            'odio_politico',
            'ameaca'
        ]
        
        self._inicializado = True
    
    def classificar(self, texto: str):
        if not texto or len(texto.strip()) < 3:
            return {
                'categoria_odio': 'neutro',
                'score': 0.0,
                'confianca': 1.0
            }
        
        inputs = self.tokenizer(
            texto,
            max_length=128,
            truncation=True,
            padding=True,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilidades = torch.softmax(logits, dim=1).cpu().numpy()[0]
            
        indice = np.argmax(probabilidades)
        confianca = probabilidades[indice]
        
        return {
            'categoria_odio': self.categorias[indice],
            'score': float(confianca),
            'confianca': float(confianca),
            'modelo_versao': 'BERTimbau_v1.0'
        }