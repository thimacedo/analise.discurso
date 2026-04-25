import { Actor } from 'apify';

async function main() {
  await Actor.init();
  const input = await Actor.getInput<{ username: string; webhookUrl: string }>();

  if (!input || !input.username || !input.webhookUrl) {
    throw new Error('Missing username or webhookUrl in input');
  }

  // Simulação de scraping (deveria usar apify/instagram-scraper ou Crawlee)
  console.log(`Scraping user: ${input.username}`);
  const data = {
    user: input.username,
    timestamp: new Date().toISOString(),
    content: "Exemplo de narrativa coletada."
  };

  // Envio via Webhook
  const response = await fetch(input.webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) throw new Error(`Webhook failed: ${response.statusText}`);

  await Actor.exit();
}

main();
