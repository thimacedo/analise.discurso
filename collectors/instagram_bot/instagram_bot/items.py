import scrapy

class InstagramBotItem(scrapy.Item):
    # Campos comuns e específicos para unificação conforme solicitado
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    post_id = scrapy.Field()
    shortcode = scrapy.Field()
    owner_username = scrapy.Field()
    text = scrapy.Field()
    timestamp = scrapy.Field()
    comment_id = scrapy.Field()
    post_shortcode = scrapy.Field()
    
    # Metadados adicionais úteis
    item_type = scrapy.Field() # 'profile', 'post', 'comment'
    updated_at = scrapy.Field()
