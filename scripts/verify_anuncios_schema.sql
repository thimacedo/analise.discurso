-- Script de Verificação do Schema da Tabela Anuncios
-- Diamond Edition PASA v16.4 Verification

DO $$ 
BEGIN
    -- 1. Verificar se a tabela anuncios existe
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'anuncios') THEN
        RAISE NOTICE 'Tabela public.anuncios não encontrada.';
    ELSE
        RAISE NOTICE 'Tabela public.anuncios encontrada.';
        
        -- 2. Verificar colunas PASA v16.4
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'anuncios' AND column_name = 'categoria_ia') THEN
            RAISE NOTICE 'Coluna categoria_ia presente.';
        ELSE
            RAISE NOTICE 'Coluna categoria_ia AUSENTE.';
        END IF;

        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'anuncios' AND column_name = 'is_hate') THEN
            RAISE NOTICE 'Coluna is_hate presente.';
        ELSE
            RAISE NOTICE 'Coluna is_hate AUSENTE.';
        END IF;

        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'anuncios' AND column_name = 'processado_ia') THEN
            RAISE NOTICE 'Coluna processado_ia presente.';
        ELSE
            RAISE NOTICE 'Coluna processado_ia AUSENTE.';
        END IF;
    END IF;
END $$;
