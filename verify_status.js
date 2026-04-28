const Database = require('better-sqlite3');
const db = new Database('data/odio_politica.db');
const row = db.prepare("SELECT id, processado_ia FROM comentarios WHERE id_externo = 'test_hate_100'").get();
console.log(JSON.stringify(row, null, 2));
const count = db.prepare("SELECT count(*) as total FROM comentarios WHERE processado_ia = 0").get();
console.log(`Backlog pendente: ${count.total}`);
