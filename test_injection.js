const Database = require('better-sqlite3');
const db = new Database('data/odio_politica.db');
db.prepare("INSERT INTO comentarios (id_externo, candidato_id, texto_bruto, processado_ia) VALUES (?, ?, ?, 0)").run('test_hate_100', 6, 'Esse povo do nordeste é tudo burro e não sabe votar, bando de miseráveis!');
console.log('✅ Alvo injetado com ID real.');
