const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
const SB_KEY = process.env.SUPABASE_KEY;
const LL_API_KEY = process.env.GROQ_API_KEY;

const headers = {
    "apikey": SB_KEY,
    "Authorization": `Bearer ${SB_KEY}`,
    "Content-Type": "application/json"
};

async function logPasa(msg) {
    console.log(`[PASA FORENSIC ${new Date().toISOString()}] ${msg}`);
}

// --- UTILITÁRIO LINGUÍSTICO (N-GRAMAS LOCAIS) ---
function getNGrams(text, n) {
    const words = text.toLowerCase().replace(/[^a-z0-9\s]/g, "").split(/\s+/).filter(w => w.length > 2);
    let ngrams = [];
    for (let i = 0; i <= words.length - n; i++) {
        ngrams.push(words.slice(i, i + n).join(" "));
    }
    return ngrams;
}

// --- FASE 1: CLASSIFICAÇÃO DE NOVOS ALVOS (GEO) ---
async function classifyNewTargets() {
    const res = await fetch(`${SB_URL}/candidatos?select=id,username,nome_completo,cargo,estado&or=(estado.is.null,estado.eq.DF)`, { headers });
    const targets = await res.json();
    if (targets.length === 0) return;

    for (const t of targets) {
        try {
            const prompt = `Analise o perfil político: "@${t.username}" (${t.nome_completo}). 
            Determine a esfera de atuação conforme o Cérebro Linguístico do projeto.
            Responda APENAS a sigla: BR (Nacional/Federal), ou a UF correspondente (ex: RN, SP, RJ).`;

            const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Authorization": `Bearer ${LLM_API_KEY}`, "Content-Type": "application/json" },
                body: JSON.stringify({
                    model: "llama-3.3-70b-versatile",
                    messages: [{ role: "user", content: forensicPrompt }],
                    temperature: 0.1,
                    response_format: { type: "json_object" }
                })
            });

            const novoEstado = data.choices[0].message.content.trim().toUpperCase().substring(0, 2);

            await fetch(`${SB_URL}/candidatos?id=eq.${t.id}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify({ estado: novoEstado, atualizado_em: new Date().toISOString() })
            });
            logPasa(`Target @${t.username} -> ${novoEstado}`);
        } catch (e) {}
    }
}

// --- FASE 2: ANÁLISE FORENSE DE NARRATIVAS (PASA) ---
async function classifyNarratives() {
    const res = await fetch(`${SB_URL}/comentarios?select=id,texto_bruto,candidato_id&categoria_ia=is.null&limit=20`, { headers });
    const comments = await res.json();
    if (comments.length === 0) return;

    logPasa(`Iniciando análise forense em ${comments.length} interações...`);
    
    for (const c of comments) {
        try {
            // Cálculo de N-gramas para detectar padrões de Bot/Script
            const trigrams = getNGrams(c.texto_bruto, 3);
            const hasRepetitivePattern = trigrams.length > 0 && new Set(trigrams).size < trigrams.length;

            const forensicPrompt = `Atue como Perito em Linguística Forense (Protocolo PASA).
            Analise o comentário político abaixo buscando:
            1. Intenção: Ofensa, Sarcasmo, Incitação, Crítica Política ou Apoio.
            2. Marcadores: Identifique verbos de comando ou adjetivação pejorativa.
            3. Script: O comentário parece automatizado/coordenado? ${hasRepetitivePattern ? "Sim (N-gramas repetitivos detectados)" : "Não"}.

            Texto: "${c.texto_bruto}"

            Responda APENAS em formato JSON:
            {"categoria": "PALAVRA", "is_bot": boolean, "analise": "BREVE_JUSTIFICATIVA"}`;

            const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Authorization": `Bearer ${LLM_API_KEY}`, "Content-Type": "application/json" },
                body: JSON.stringify({
                    model: "llama-3.3-70b-versatile",
                    messages: [{ role: "user", content: forensicPrompt }],
                    temperature: 0.1,
                    response_format: { type: "json_object" }
                })
            });

            
            const data = await response.json();
            const result = JSON.parse(data.choices[0].message.content);
            
            // Mapeamento para o banco
            const finalCat = result.categoria.replace(/[^a-zA-Z]/g, "");
            const isHate = ["Ofensa", "Sarcasmo", "Incitacao", "Odio", "Ironia"].includes(finalCat);

            await fetch(`${SB_URL}/comentarios?id=eq.${c.id}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify({ 
                    categoria_ia: finalCat, 
                    is_hate: isHate, 
                    is_bot: result.is_bot,
                    analise_forense: result.analise,
                    processado_em: new Date().toISOString() 
                })
            });
            logPasa(`@${c.candidato_id} [${finalCat}] | Bot: ${result.is_bot}`);
        } catch (e) {
            logPasa(`Erro narrativa ID ${c.id}: ${e.message}`);
        }
    }
}

(async () => {
    while (true) {
        try {
            await classifyNewTargets();
            await classifyNarratives();
        } catch (e) {
            logPasa(`Erro geral: ${e.message}`);
        }
        await new Promise(r => setTimeout(r, 60000));
    }
})();
