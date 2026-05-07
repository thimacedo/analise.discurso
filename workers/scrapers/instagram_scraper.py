# instagram_scraper.py
import requests
import json
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger("InstagramScraper")

class InstagramScraper:
    def __init__(self, target_profile: str, max_retries: int = 3):
        self.target_profile = target_profile
        self.max_retries = max_retries
        self.base_url = f"https://www.instagram.com/{target_profile}/?__a=1&__d=dis"
        # Em produção, adicionar headers rotativos e controle de sessão
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

    def fetch_recent_posts(self) -> List[Dict]:
        """Extrai os metadados dos posts recentes, com resiliência de retentativas."""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.base_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Navegação robusta na estrutura do JSON do Instagram (Pode variar; estrutura simulada para extração profunda)
                user_data = data.get("graphql", {}).get("user", {})
                timeline = user_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
                
                posts = []
                for edge in timeline:
                    node = edge.get("node", {})
                    post_data = {
                        "id": node.get("id"),
                        "shortcode": node.get("shortcode"),
                        "text": node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", ""),
                        "timestamp": node.get("taken_at_timestamp"),
                        "comments_count": node.get("edge_media_to_comment", {}).get("count", 0),
                    }
                    posts.append(post_data)
                
                logger.info(f"[{self.target_profile}] Extracted {len(posts)} posts successfully.")
                return posts

            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                logger.warning(f"Attempt {attempt + 1} failed for {self.target_profile}: {e}")
                time.sleep(2 ** attempt)  # Backoff exponencial

        logger.error(f"Failed to fetch posts for {self.target_profile} after {self.max_retries} attempts.")
        return []

    def fetch_comments(self, post_shortcode: str, max_comments: int = 50) -> List[Dict]:
         """Simula a extração de comentários de um post específico."""
         # Lógica real de paginação GraphQL iria aqui.
         logger.info(f"Extracting comments for post {post_shortcode}...")
         return [
             {"id": f"c_{i}", "text": f"Simulated comment {i} for {post_shortcode}", "author": f"user_{i}"}
             for i in range(min(max_comments, 5)) # Simulação
         ]