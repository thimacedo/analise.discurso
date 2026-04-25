-- Evolução do Schema Forense v7.0
ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS prioridade INTEGER DEFAULT 3;
ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS categoria TEXT DEFAULT 'SATELITE';
ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS cenario TEXT DEFAULT 'BRASIL';
ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS cargo_pretendido TEXT;

-- Inserir/Atualizar Monitorados Prioritários
INSERT INTO candidatos (username, prioridade, categoria, cenario, cargo_pretendido)
VALUES 
('lulaoficial', 1, 'CANDIDATO_ATIVO', 'BRASIL', 'Presidente'),
('flaviobolsonaro', 1, 'CANDIDATO_ATIVO', 'BRASIL', 'Presidente'),
('allysonbezerra.rn', 1, 'CANDIDATO_ATIVO', 'RN', 'Governador'),
('alvarodiasrn', 1, 'CANDIDATO_ATIVO', 'RN', 'Governador'),
('rogeriomarinho', 1, 'CANDIDATO_ATIVO', 'RN', 'Governador'),
('fatimabezerrapetista', 1, 'CANDIDATO_ATIVO', 'RN', 'Senado'),
('styvensonvalentim', 2, 'CANDIDATO_ATIVO', 'RN', 'Senado'),
('nikolasferreirainfo', 1, 'RELEVANTE_NACIONAL', 'BRASIL', 'Deputado'),
('erikahiltonoficial', 1, 'RELEVANTE_NACIONAL', 'BRASIL', 'Deputada'),
('jones.manoel', 2, 'RELEVANTE_NACIONAL', 'BRASIL', 'Liderança')
ON CONFLICT (username) DO UPDATE SET 
prioridade = EXCLUDED.prioridade,
categoria = EXCLUDED.categoria,
cenario = EXCLUDED.cenario,
cargo_pretendido = EXCLUDED.cargo_pretendido;
