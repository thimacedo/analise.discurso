SELECT
    p.proname AS function_name,
    n.nspname AS schema_name,
    pg_get_function_identity_arguments(p.oid) AS identity_arguments,
    pg_get_function_arguments(p.oid) AS arguments,
    p.prorettype::regtype AS return_type
FROM
    pg_catalog.pg_proc p
JOIN
    pg_catalog.pg_namespace n ON n.oid = p.pronamespace
WHERE
    p.proname = 'broadcast_changes' AND n.nspname = 'realtime';