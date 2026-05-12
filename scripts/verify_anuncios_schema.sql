-- Check if the required PASA fields exist in the anuncios table
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'anuncios' 
AND column_name IN ('corpo_anuncio', 'categoria_ia', 'confianca_ia', 'is_hate', 'processado_ia');