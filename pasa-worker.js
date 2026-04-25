const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
const SB_KEY = process.env.SUPABASE_KEY;
const LL_API_KEY = process.env.GROQ_API_KEY;

const headers = {
    "apikey": SB_KEY,
    "Authorization": `Bearer ${SB_KEY}`,
    "Content-Type": "application/json"
};

async function logPasa(msg) {
    console.log(`[PASA+GEO WORKER ${new Date().toISOString()}] ${msg}`);
}

// --- FASE 1: CLASSIFICAÇÃO DE NOVOS ALVOS (GEO/CARGO) ---
async function classifyNewTargets() {
    const res = await fetch(`${SB_URL}/candidatos?select=id,username,nome_completo,cargo,estado&or=(estado.is.null,estado.eq.DF)`, { headers });
    const targets = await res.json();

    if (targets.length === 0) return;

    logPasa(`Revisando geolocalização de ${targets.length} alvos...`);
    
    for (const t of targets) {
        try {
            const prompt = `Analise o perfil político: "@${t.username}" (${t.nome_completo}). 
            Se for figura nacional/presidenciável/ministro/STF, responda: BR. 
            Se for regional, responda a UF (ex: RN, SP, RJ). 
            Responda APENAS a sigla.`;

            const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Authorization": `Bearer ${LL_API_KEY}`, "Content-Type": "application/json" },
                body: JSON.stringify({
                    model: "gemma2-9b-it",
                    messages: [{ role: "user", content: prompt }],
                    temperature: 0.1
                })
            });
            const data = await response.json();
            const novoEstado = data.choices[0].message.content.trim().toUpperCase().substring(0, 2);

            await fetch(`${SB_URL}/candidatos?id=eq.${t.id}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify({ estado: novoEstado, atualizado_em: new Date().toISOString() })
            });
            logPasa(`Target @${t.username} reclassificado para: ${novoEstado}`);
        } catch (e) {
            logPasa(`Erro ao classificar target @${t.username}: ${e.message}`);
        }
    }
}

// --- FASE 2: CLASSIFICAÇÃO DE NARRATIVAS (PASA) ---
async function classifyNarratives() {
    const res = await fetch(`${SB_URL}/comentarios?select=id,texto_bruto,candidato_id&categoria_ia=is.null&limit=20`, { headers });
    const comments = await res.json();

    if (comments.length === 0) return;

    logPasa(`Processando ${comments.length} narrativas pendentes...`);
    
    for (const c of comments) {
        try {
            const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Authorization": `Bearer ${LL_API_KEY}`, "Content-Type": "application/json" },
                body: JSON.stringify({
                    model: "gemma2-9b-it",
                    messages: [
                        { role: "system", content: "Classifique em uma palavra: Odio, Ironia, Critica, Neutro ou Apoio. APENAS A PALAVRA." },
                        { role: "user", content: c.texto_bruto }
                    ],
                    temperature: 0.1
                })
            });
            const data = await response.json();
            const category = data.choices[0].message.content.trim().replace(/[^a-zA-Z]/g, "");
            const isHate = category === "Odio" || category === "Ironia";

            await fetch(`${SB_URL}/comentarios?id=eq.${c.id}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify({ categoria_ia: category, is_hate: isHate, processado_em: new Date().toISOString() })
            });
        } catch (e) {
            logPasa(`Erro narrativa ID ${c.id}: ${e.message}`);
        }
    }
}

// --- LOOP PRINCIPAL ---
(async () => {
    while (true) {
        try {
            await classifyNewTargets(); // Primeiro limpa a geolocalização/estados
            await classifyNarratives();  // Depois processa o sentimento
        } catch (e) {
            logPasa(`Erro geral no worker: ${e.message}`);
        }
        await new Promise(r => setTimeout(r, 60000)); // Polling a cada 60s
    }
})();
