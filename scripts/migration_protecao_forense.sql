-- scripts/migration_protecao_forense.sql
ALTER TABLE analises 
ADD COLUMN IF NOT EXISTS confirmado_por UUID,
ADD COLUMN IF NOT EXISTS data_confirmacao TIMESTAMP WITH TIME ZONE;

CREATE OR REPLACE FUNCTION validar_alteracao_falso_positivo()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'falso_positivo' AND OLD.status = 'positivo' THEN
        IF NEW.confirmado_por IS NULL THEN
            RAISE EXCEPTION 'Apenas usuários autorizados podem marcar falsos positivos.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validar_falso_positivo ON analises;
CREATE TRIGGER trg_validar_falso_positivo
BEFORE UPDATE ON analises
FOR EACH ROW
EXECUTE FUNCTION validar_alteracao_falso_positivo();
