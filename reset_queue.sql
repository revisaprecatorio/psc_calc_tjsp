-- ============================================================================
-- Script: reset_queue.sql
-- Descrição: Reseta o status da fila de processamento para permitir 
--            reprocessamento de jobs
-- Uso: psql -h 72.60.62.124 -p 5432 -U admin -d n8n -f reset_queue.sql
-- ============================================================================

-- 1. Ver estatísticas atuais da fila
SELECT 
    COUNT(*) as total_registros,
    COUNT(*) FILTER (WHERE status = TRUE) as processados,
    COUNT(*) FILTER (WHERE status = FALSE OR status IS NULL) as pendentes
FROM consultas_esaj;

-- 2. Ver últimos 10 registros processados
SELECT id, cpf, status, created_at, updated_at 
FROM consultas_esaj 
WHERE status = TRUE 
ORDER BY id DESC 
LIMIT 10;

-- 3. OPÇÃO A: Resetar TODOS os registros para reprocessamento
-- CUIDADO: Isso vai marcar todos como pendentes novamente
-- UPDATE consultas_esaj SET status = FALSE;

-- 4. OPÇÃO B: Resetar apenas os últimos N registros
-- Útil para reprocessar jobs recentes
-- UPDATE consultas_esaj 
-- SET status = FALSE 
-- WHERE id IN (
--     SELECT id FROM consultas_esaj 
--     WHERE status = TRUE 
--     ORDER BY id DESC 
--     LIMIT 10
-- );

-- 5. OPÇÃO C: Resetar registros específicos por ID
-- Substitua os IDs pelos que você quer reprocessar
-- UPDATE consultas_esaj 
-- SET status = FALSE 
-- WHERE id IN (30, 31, 32);

-- 6. OPÇÃO D: Resetar registros de um CPF específico
-- UPDATE consultas_esaj 
-- SET status = FALSE 
-- WHERE cpf = '07620857893';

-- 7. Verificar resultado após UPDATE
SELECT 
    COUNT(*) as total_registros,
    COUNT(*) FILTER (WHERE status = TRUE) as processados,
    COUNT(*) FILTER (WHERE status = FALSE OR status IS NULL) as pendentes
FROM consultas_esaj;

-- 8. Ver próximos registros que serão processados
SELECT id, cpf, status 
FROM consultas_esaj 
WHERE status = FALSE OR status IS NULL 
ORDER BY id 
LIMIT 5;
