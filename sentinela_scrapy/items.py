import scrapy
from datetime import datetime

class InstagramCommentItem(scrapy.Item):
    """Item padronizado para todos os Tiers."""
    
    # Identificadores
    comment_id = scrapy.Field()
    post_shortcode = scrapy.Field()
    
    # Dados do usuário
    ownerUsername = scrapy.Field()
    
    # Conteúdo
    text = scrapy.Field()
    created_at = scrapy.Field()
    
    # Métricas
    like_count = scrapy.Field()
    
    # Metadata
    candidato_id = scrapy.Field()
    tier_used = scrapy.Field()  # Qual tier foi usado (1, 2, 3 ou 4)
    scraped_at = scrapy.Field()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['scraped_at'] = datetime.now().isoformat()
        if 'tier_used' not in kwargs:
            self['tier_used'] = 0
