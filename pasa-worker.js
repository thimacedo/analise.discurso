const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
const SB_KEY = process.env.SUPABASE_KEY; // Service Role Key para escrita
const LLM_API_KEY = process.env.GROQ_API_KEY; // Usando Groq/Gemma para velocidade

const headers = {
    "apikey": SB_KEY,
    "Authorization": `Bearer ${SB_KEY}`,
    "Content-Type": "application/json"
};

async function logPasa(msg) {
    console.log(`[PASA WORKER ${new Date().toISOString()}] ${msg}`);
}

async function getPendingComments() {
    const res = await fetch(`${SB_URL}/comentarios?select=id,texto_bruto,candidato_id&categoria_ia=is.null&limit=20`, { headers });
    return await res.json();
}

async function classifyText(text) {
    // Protocolo PASA: Classificação estatística de narrativas
    try {
        const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${LLM_API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: "gemma2-9b-it",
                messages: [
                    { role: "system", content: "Classifique o comentário político em uma única palavra: Odio, Ironia, Critica, Neutro ou Apoio. Responda APENAS a palavra." },
                    { role: "user", content: text }
                ],
                temperature: 0.1
            })
        });
        const data = await response.json();
        return data.choices[0].message.content.trim().replace(/[.]/g, "");
    } catch (e) {
        return "Neutro";
    }
}

async function updateComment(id, category) {
    const isHate = category === "Odio" || category === "Ironia";
    await fetch(`${SB_URL}/comentarios?id=eq.${id}`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({
            categoria_ia: category,
            is_hate: isHate,
            processado_em: new Date().toISOString()
        })
    });
}

async function runPasaCycle() {
    logPasa("Iniciando ciclo de avaliação...");
    const comments = await getPendingComments();
    
    if (comments.length === 0) {
        logPasa("Nenhum dado pendente. Aguardando...");
        return;
    }

    logPasa(`Processando ${comments.length} interações...`);
    for (const c of comments) {
        const category = await classifyText(c.texto_bruto);
        await updateComment(c.id, category);
        logPasa(`@${c.candidato_id} -> ${category}`);
    }
    logPasa("Ciclo finalizado.");
}

// Execução Contínua (Loop)
(async () => {
    while (true) {
        try {
            await runPasaCycle();
        } catch (e) {
            logPasa(`Erro no ciclo: ${e.message}`);
        }
        await new Promise(r => setTimeout(r, 60000)); // Espera 1 minuto entre checagens
    }
})();
