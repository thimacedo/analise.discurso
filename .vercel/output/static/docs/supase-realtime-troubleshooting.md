# Erro de Broadcast no Supabase Realtime com fetch_pending.py

## Descrição do Problema
O script `fetch_pending.py` falha ao tentar processar comentários devido a um erro de broadcast no Supabase Realtime. O erro específico é `42883: function realtime.broadcast_changes(...) does not exist`. Este erro impede a atualização do status dos comentários no sistema.

## Contexto da Falha
O erro ocorre quando o trigger `realtime_broadcast_comentarios` (definido no schema `public` para a tabela `comentarios`) tenta invocar a função `realtime.broadcast_changes()` (esperada no schema `realtime`).

## Investigação Realizada
1.  **Verificação da Função:** Foi confirmado que a função `realtime.broadcast_changes()` existe no schema `realtime`.
2.  **Análise da Assinatura da Função:** A assinatura da função `realtime.broadcast_changes()` parece ser `void`, indicando que ela não aceita argumentos explícitos ou espera um formato específico que não está sendo fornecido.
3.  **Análise do Trigger:** O trigger `realtime_broadcast_comentarios` está configurado para chamar `realtime.broadcast_changes()`. A persistência do erro `42883` sugere uma incompatibilidade de assinatura entre o que o trigger espera e o que a função realmente aceita. Logs anteriores indicaram uma possível confusão com uma função `_realtime_broadcast_changes()` (com underscore), que não existe.
4.  **Verificação da Publicação Realtime:** A tabela `comentarios` já está corretamente associada à publicação `supabase_realtime`. Tentativas de adicioná-la novamente (`ALTER PUBLICATION supabase_realtime ADD TABLE comentarios;`) resultaram no erro `42704: relation "comentarios" is already member of publication`.
5.  **Isolamento do Problema:** O script `fetch_pending.py` não chama a função `realtime.broadcast_changes()` diretamente; o problema é totalmente isolado à configuração do Supabase Realtime e seus triggers/funções.

## Tentativas de Resolução (Sem Sucesso)
- Tentar recriar o trigger `realtime_broadcast_comentarios` para chamar `realtime.broadcast_changes()` com a assinatura esperada, mas o erro `42883` persistiu.
- `ALTER PUBLICATION supabase_realtime ADD TABLE comentarios;` (Erro: `42704`)

## Estado Atual e Próximos Passos
A causa raiz mais provável é uma incompatibilidade de assinatura entre o trigger `realtime_broadcast_comentarios` e a função `realtime.broadcast_changes()`.

Os próximos passos para a resolução incluem:
- Investigar a fundo a assinatura exata da função `realtime.broadcast_changes()` e como ela interage com triggers.
- Adaptar o trigger ou criar uma função wrapper se necessário.

Este documento será atualizado com a solução definitiva quando encontrada.
