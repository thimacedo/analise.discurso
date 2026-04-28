const Database = require('better-sqlite3');
const axios = require('axios');
require('dotenv').config();
const fs = require('fs');

const DB_PATH = 'E:/projetos/sentinela-democratica/data/odio_politica.db';
const OLLAMA_URL = 'http://localhost:11434/api/generate';
const MODEL_TRIAGE = 'qwen2.5:3b';
const MODEL_EXPERT = 'gemma:2b';

const log = (msg) => {
    const entry = `${new Date().toISOString()} [INFO] ${msg}\n`;
    console.log(entry.trim());
    try { fs.appendFileSync('logs/intelligence_js.log', entry); } catch (e) {}
};

const callOllama = async (model, prompt, systemRules) => {
    try {
        const payload = {
            model: model,
            prompt: `DIRETRIZES: ${systemRules}\n\nENTRADA: '${prompt}'`,
            stream: false,
            format: 'json'
        };
        const res = await axios.post(OLLAMA_URL, payload, { timeout: 120000 });
        const rawResponse = res.data.response;
        log(`[RAW] Resposta do modelo ${model}: ${rawResponse.substring(0, 100)}...`);
        return JSON.parse(rawResponse);
    } catch (e) {
        log(`[-] Erro no modelo ${model}: ${e.message}`);
        return null;
    }
};

const analyze = async (text) => {
    // Para teste: Forçando Expert em comentários suspeitos de ódio regional
    const lowerText = text.toLowerCase();
    const isRegionalSuspect = lowerText.includes('nordeste') || lowerText.includes('analfabeto') || lowerText.includes('votar');

    if (isRegionalSuspect) {
        log(`🎯 [EXPERT-FORCED] Detectado gatilho regional: ${text.substring(0, 30)}`);
        const systemExpert = "Aja como Perito Forense Sênior (PASA v16.3). ANALISE: Performatividade, Falácias (Ad Hominem), Vetor de Fúria. CATEGORIAS: XENOFOBIA_REGIONAL, RACISMO_RELIGIOSO, VIOLÊNCIA_GÊNERO, MILICIA_DIGITAL. Retorne JSON: {is_hate: bool, categoria: string, falacia: string, analise_pericial: string}";
        return await callOllama(MODEL_EXPERT, text, systemExpert);
    }

    // Fluxo normal para outros casos
    return await callOllama(MODEL_TRIAGE, text, "Triagem Forense. JSON: {is_hate: bool, categoria: string, needs_expert: bool}");
};

const run = async () => {
    log('🚀 Sentinela Intelligence JS Engine v16.5.2 (Rigor Expert) Ativada.');
    const db = new Database(DB_PATH);
    while (true) {
        try {
            const rows = db.prepare('SELECT id, texto_bruto FROM comentarios WHERE processado_ia = 0 LIMIT 5').all();
            if (rows.length === 0) { await new Promise(r => setTimeout(r, 5000)); continue; }

            for (const row of rows) {
                log(`[-] Processando ID ${row.id}...`);
                const res = await analyze(row.texto_bruto);
                if (!res) continue;
                
                db.prepare(`
                    UPDATE comentarios 
                    SET processado_ia = 1, is_hate = ?, categoria_ia = ?, 
                        analise_pericial = ?, data_processamento = ? 
                    WHERE id = ?
                `).run(
                    res.is_hate ? 1 : 0, 
                    res.categoria || 'NEUTRO', 
                    res.analise_pericial || res.falacia || 'Análise via Expert Engine', 
                    new Date().toISOString(), 
                    row.id
                );
                log(`✅ ID ${row.id} -> ${res.categoria || 'NEUTRO'}`);
            }
        } catch (e) { log(`❌ Erro no ciclo: ${e.message}`); await new Promise(r => setTimeout(r, 5000)); }
    }
};

run();
