import pandas as pd
from instagrapi import Client
from datetime import datetime, timedelta
import time
import logging

logging.basicConfig(level=logging.INFO)

class InstagramCollector:
    def __init__(self, username=None, password=None):
        self.client = Client()
        if username and password:
            self.client.login(username, password)
        self.comments_data = []
    
    def collect_comments(self, media_url, max_comments=100):
        """
        Coleta comentários de uma postagem específica
        Seguindo a metodologia de coleta de corpus do prof. Vichi
        """
        media_id = self.client.media_id(media_url)
        comments = self.client.media_comments(media_id, amount=max_comments)
        
        for comment in comments:
            self.comments_data.append({
                'text': comment.text,
                'username': comment.user.username,
                'timestamp': comment.timestamp,
                'like_count': comment.like_count,
                'media_id': media_id
            })
        
        return pd.DataFrame(self.comments_data)
    
    def collect_politician_posts(self, username, posts_count=10):
        """Coleta comentários de posts de um político específico"""
        user_id = self.client.user_id_from_username(username)
        medias = self.client.user_medias(user_id, posts_count)
        
        all_comments = []
        for media in medias:
            comments = self.client.media_comments(media.id, amount=200)
            for comment in comments:
                all_comments.append({
                    'text': comment.text,
                    'username': comment.user.username,
                    'post_caption': media.caption_text if media.caption_text else '',
                    'post_likes': media.like_count,
                    'post_comments': media.comment_count,
                    'timestamp': comment.timestamp,
                    'candidate': username
                })
            time.sleep(1)  # Evitar rate limiting
        
        df = pd.DataFrame(all_comments)
        df.to_csv(f'corpus_{username}.csv', index=False, encoding='utf-8')
        return df

# Exemplo de uso
if __name__ == "__main__":
    collector = InstagramCollector()
    # Coleta para candidatos específicos
    candidates = ["candidato_a", "candidato_b", "candidato_c"]
    for candidate in candidates:
        try:
            df = collector.collect_politician_posts(candidate, posts_count=20)
            print(f"Coletados {len(df)} comentários de @{candidate}")
        except Exception as e:
            print(f"Erro ao coletar @{candidate}: {e}")