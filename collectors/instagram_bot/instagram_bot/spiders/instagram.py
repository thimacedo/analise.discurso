import os
import json
import scrapy
from datetime import datetime
from instagram_bot.items import InstagramProfileItem, InstagramPostItem, InstagramCommentItem

class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["instagram.com"]
    
    def __init__(self, usernames=None, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.usernames = usernames.split(",") if usernames else []
        self.session_id = os.environ.get("INSTAGRAM_SESSIONID")
        self.cookies = {"sessionid": self.session_id} if self.session_id else {}

    def start_requests(self):
        if not self.session_id:
            self.logger.error("INSTAGRAM_SESSIONID not found in environment.")
            return

        for username in self.usernames:
            # Resolve username to user_id (web approach or specific API)
            # Here we'll use a common mobile API endpoint for user info
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            yield scrapy.Request(
                url=url,
                cookies=self.cookies,
                callback=self.parse_profile,
                meta={'username': username}
            )

    def parse_profile(self, response):
        data = json.loads(response.text)
        user = data.get('data', {}).get('user', {})
        if not user:
            self.logger.warning(f"Could not find user data for {response.meta['username']}")
            return

        user_id = user.get('id')
        
        profile = InstagramProfileItem(
            id=user_id,
            username=user.get('username'),
            full_name=user.get('full_name'),
            biography=user.get('biography'),
            follower_count=user.get('edge_followed_by', {}).get('count'),
            following_count=user.get('edge_follow', {}).get('count'),
            media_count=user.get('edge_owner_to_timeline_media', {}).get('count'),
            external_url=user.get('external_url'),
            is_private=user.get('is_private'),
            is_verified=user.get('is_verified'),
            profile_pic_url=user.get('profile_pic_url_hd'),
        )
        yield profile

        # Get feed
        feed_url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/"
        yield scrapy.Request(
            url=feed_url,
            cookies=self.cookies,
            callback=self.parse_feed,
            meta={'user_id': user_id}
        )

    def parse_feed(self, response):
        data = json.loads(response.text)
        items = data.get('items', [])
        
        for item in items:
            media_id = item.get('id')
            pk = item.get('pk')
            
            post = InstagramPostItem(
                id=media_id,
                pk=pk,
                code=item.get('code'),
                user_id=item.get('user', {}).get('pk'),
                caption_text=item.get('caption', {}).get('text') if item.get('caption') else None,
                media_type=item.get('media_type'),
                comment_count=item.get('comment_count'),
                like_count=item.get('like_count'),
                view_count=item.get('view_count'),
                taken_at=datetime.fromtimestamp(item.get('taken_at')).isoformat() if item.get('taken_at') else None,
                product_type=item.get('product_type'),
                video_duration=item.get('video_duration'),
            )
            yield post

            # Get comments for this post
            comments_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
            yield scrapy.Request(
                url=comments_url,
                cookies=self.cookies,
                callback=self.parse_comments,
                meta={'post_id': media_id}
            )

        # Pagination for feed
        next_max_id = data.get('next_max_id')
        if next_max_id:
            user_id = response.meta['user_id']
            next_url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/?max_id={next_max_id}"
            yield scrapy.Request(
                url=next_url,
                cookies=self.cookies,
                callback=self.parse_feed,
                meta={'user_id': user_id}
            )

    def parse_comments(self, response):
        data = json.loads(response.text)
        comments = data.get('comments', [])
        post_id = response.meta['post_id']

        for comment in comments:
            item = InstagramCommentItem(
                id=str(comment.get('pk')),
                pk=comment.get('pk'),
                text=comment.get('text'),
                user_id=comment.get('user', {}).get('pk'),
                post_id=post_id,
                created_at=datetime.fromtimestamp(comment.get('created_at')).isoformat() if comment.get('created_at') else None,
            )
            yield item
