const Database = require('better-sqlite3');
const db = new Database('data/odio_politica.db');
const rows = db.prepare("SELECT texto_bruto, categoria_ia, analise_pericial FROM comentarios WHERE id_externo = 'test_hate_100'").all();
console.log(JSON.stringify(rows, null, 2));
