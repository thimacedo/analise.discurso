# core/behavior_engine.py
import random
import asyncio
from playwright.async_api import Page

class BehaviorEngine:
    """Simulador de comportamento humano para evasão heurística (PASA v16.4)"""
    def __init__(self, page: Page):
        self.page = page

    async def random_scroll(self):
        """Realiza scrolls erráticos para simular leitura humana."""
        steps = random.randint(3, 7)
        for _ in range(steps):
            scroll_amount = random.randint(300, 700)
            await self.page.mouse.wheel(0, scroll_amount)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            if random.random() > 0.8:
                await self.page.mouse.wheel(0, -200)

    async def human_move_to(self, selector: str):
        """Move o mouse de forma não-linear até um elemento."""
        element = await self.page.wait_for_selector(selector)
        box = await element.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            await self.page.mouse.move(x + random.randint(-5, 5), y + random.randint(-5, 5), steps=10)

    async def simulate_idle(self):
        """Simula o tempo de 'pensamento' do usuário."""
        if random.random() > 0.7:
            await asyncio.sleep(random.uniform(2.0, 5.0))
