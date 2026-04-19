import scrapy

class InstagramProfileItem(scrapy.Item):
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()

class InstagramPostItem(scrapy.Field):
    post_id = scrapy.Field()
    shortcode = scrapy.Field()
    owner_username = scrapy.Field()
    text = scrapy.Field()
    timestamp = scrapy.Field()

class InstagramCommentItem(scrapy.Item):
    comment_id = scrapy.Field()
    post_shortcode = scrapy.Field()
    owner_username = scrapy.Field()
    text = scrapy.Field()
    timestamp = scrapy.Field()
