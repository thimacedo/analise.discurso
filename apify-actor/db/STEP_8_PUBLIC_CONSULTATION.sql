-- ==========================================================
-- INOVASYS - CONSULTA PÚBLICA SEGURA (v2.0)
-- Função RPC para validar autenticidade de sentenças
-- ==========================================================

CREATE OR REPLACE FUNCTION public.consultar_sentenca_publica(p_numero_processo TEXT, p_codigo_validacao TEXT)
RETURNS JSONB AS $$
DECLARE
    v_resultado JSONB;
BEGIN
    SELECT jsonb_build_object(
        'numero_processo', p.numero_processo,
        'requerente_nome', p.requerente_nome,
        'requerido_nome', p.requerido_nome,
        'status', p.status,
        'data_conclusao', p.updated_at,
        'conteudo_html', da.html_final,
        'assinado_por', da.signatario_nome,
        'hash_validacao', da.hash_assinatura
    ) INTO v_resultado
    FROM public.processos p
    JOIN public.documentos_assinados da ON da.processo_id = p.id
    WHERE p.numero_processo = p_numero_processo
      AND da.hash_assinatura = p_codigo_validacao
      AND p.status IN ('Concluído', 'Arquivado')
      AND da.documento_tipo = 8; -- Tipo 8 é Sentença Arbitral

    IF v_resultado IS NULL THEN
        RETURN jsonb_build_object('error', 'Documento não encontrado ou código inválido.');
    END IF;

    RETURN v_resultado;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
