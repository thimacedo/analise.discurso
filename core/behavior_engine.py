import random
import asyncio
from playwright.async_api import Page

class BehaviorEngine:
    def __init__(self, page: Page):
        self.page = page

    async def random_scroll(self):
        for _ in range(random.randint(2, 5)):
            await self.page.mouse.wheel(0, random.randint(300, 600))
            await asyncio.sleep(random.uniform(1, 2))

    async def simulate_idle(self):
        await asyncio.sleep(random.uniform(2, 4))
