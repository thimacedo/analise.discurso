import express from 'express';
import { createClient } from '@supabase/supabase-js';
import Groq from 'groq-sdk';

const app = express();
app.use(express.json());

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_KEY!);
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

app.post('/webhook', async (req, res) => {
  const { user, content } = req.body;
  
  // Análise com Groq
  const chatCompletion = await groq.chat.completions.create({
    messages: [{ role: 'user', content: `Analise a narrativa de: ${content}` }],
    model: 'llama3-8b-8192',
  });

  const analysis = chatCompletion.choices[0].message.content;

  // Persistência
  await supabase.from('narrativas').insert({ user, content, analysis });

  res.status(200).send('OK');
});

app.listen(3000, () => console.log('Worker rodando na porta 3000'));
