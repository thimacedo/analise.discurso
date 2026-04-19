import scrapy

class InstagramProfileItem(scrapy.Item):
    id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    biography = scrapy.Field()
    follower_count = scrapy.Field()
    following_count = scrapy.Field()
    media_count = scrapy.Field()
    external_url = scrapy.Field()
    is_private = scrapy.Field()
    is_verified = scrapy.Field()
    profile_pic_url = scrapy.Field()
    updated_at = scrapy.Field()

class InstagramPostItem(scrapy.Item):
    id = scrapy.Field()
    pk = scrapy.Field()
    code = scrapy.Field()
    user_id = scrapy.Field()
    caption_text = scrapy.Field()
    media_type = scrapy.Field()
    comment_count = scrapy.Field()
    like_count = scrapy.Field()
    view_count = scrapy.Field()
    taken_at = scrapy.Field()
    product_type = scrapy.Field()
    video_duration = scrapy.Field()
    updated_at = scrapy.Field()

class InstagramCommentItem(scrapy.Item):
    id = scrapy.Field()
    pk = scrapy.Field()
    text = scrapy.Field()
    user_id = scrapy.Field()
    post_id = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
