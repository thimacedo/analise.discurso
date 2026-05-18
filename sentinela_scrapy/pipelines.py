import re
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class QualityGatePipeline:
    """Filtra comentários de baixa qualidade."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        text = adapter.get('text', '').strip()
        
        # Validações
        if not text:
            raise DropItem("Comentário vazio")
        
        if len(text) < 3:
            raise DropItem("Comentário muito curto")
        
        # Remove apenas emojis
        if re.fullmatch(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+', text):
            raise DropItem("Apenas emojis")
        
        # Normaliza espaços
        adapter['text'] = re.sub(r'\s+', ' ', text).strip()
        
        return item

class CleanCommentPipeline:
    """Quality Gate v2 integrado ao Scrapy."""
    
    # Padrões de lixo de UI do Instagram para descartar
    UI_TRASH_PATTERNS = [
        r'^\d+\s*(h|d|sem|min)$',  # "3 h", "2 d"
        r'^(Ver tradução|Ver comentário|Respondendo|Ver resposta)$',
        r'^\.{2,}$',
        r'^[👍❤️😂😢😧😡🥺]\s*\d*$',  # Apenas emojis
    ]

    def process_item(self, item, spider):
        text = item.get('text', '').strip()
        
        # 2. Padrões de UI
        for pattern in self.UI_TRASH_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                raise DropItem(f"Descartado: Lixo de UI ('{text}')")
                
        return item
