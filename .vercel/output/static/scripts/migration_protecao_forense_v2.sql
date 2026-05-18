-- scripts/migration_protecao_forense_v2.sql
ALTER TABLE comentarios 
ADD COLUMN IF NOT EXISTS confirmado_por UUID,
ADD COLUMN IF NOT EXISTS data_confirmacao TIMESTAMP WITH TIME ZONE;

CREATE OR REPLACE FUNCTION validar_alteracao_falso_positivo_manual()
RETURNS TRIGGER AS $$
BEGIN
    -- Se o novo valor for FALSO_POSITIVO_MANUAL e era algo diferente antes
    IF NEW.categoria_ia = 'FALSO_POSITIVO_MANUAL' AND (OLD.categoria_ia IS NULL OR OLD.categoria_ia != 'FALSO_POSITIVO_MANUAL') THEN
        -- Verifica se o campo de confirmação foi preenchido
        IF NEW.confirmado_por IS NULL THEN
            RAISE EXCEPTION 'ERRO FORENSE: Apenas usuários autenticados podem marcar FALSO_POSITIVO_MANUAL. O campo confirmado_por é obrigatório.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validar_falso_positivo_manual ON comentarios;
CREATE TRIGGER trg_validar_falso_positivo_manual
BEFORE UPDATE ON comentarios
FOR EACH ROW
EXECUTE FUNCTION validar_alteracao_falso_positivo_manual();
