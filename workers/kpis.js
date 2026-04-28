const Database = require('better-sqlite3');
const axios = require('axios');
require('dotenv').config();
const fs = require('fs');

const DB_PATH = 'E:/projetos/sentinela-democratica/data/odio_politica.db';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;

const log = (msg) => {
    const entry = `${new Date().toISOString()} [KPI] ${msg}\n`;
    console.log(entry.trim());
    try {
        fs.appendFileSync('logs/kpis_js.log', entry);
    } catch (e) {}
};

const syncKpis = async () => {
    log('📊 Iniciando sincronização de KPIs...');
    try {
        const db = new Database(DB_PATH);
        const stats = db.prepare('SELECT candidato_id, COUNT(*) as total, SUM(CASE WHEN is_hate = 1 THEN 1 ELSE 0 END) as odio FROM comentarios GROUP BY candidato_id').all();
        
        const headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": `Bearer ${SUPABASE_KEY}`,
            "Content-Type": "application/json"
        };

        for (const s of stats) {
            if (!s.candidato_id) continue;
            const payload = {
                comentarios_totais_count: s.total,
                comentarios_odio_count: s.odio || 0,
                last_kpi_sync: new Date().toISOString()
            };
            
            try {
                await axios.patch(`${SUPABASE_URL}/rest/v1/candidatos?id=eq.${s.candidato_id}`, payload, { headers });
                log(`✅ Sincronizado: ${String(s.candidato_id).substring(0,8)} (${s.odio || 0}/${s.total})`);
            } catch (apiErr) {
                log(`[-] Erro no Patch do Candidato ${s.candidato_id}: ${apiErr.message}`);
            }
        }
        db.close();
    } catch (e) {
        log(`❌ Erro KPI Sync: ${e.message}`);
    }
};

const run = async () => {
    log('🚀 KPI Orchestrator JS v16.5.1 Ativado.');
    while (true) {
        await syncKpis();
        await new Promise(r => setTimeout(r, 600000)); // 10 min
    }
};

run();
