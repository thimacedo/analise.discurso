const Database = require('better-sqlite3');
const db = new Database('data/odio_politica.db');
db.prepare("UPDATE comentarios SET processado_ia = 0 WHERE id_externo = 'test_hate_100'").run();
console.log('✅ Alvo resetado.');
