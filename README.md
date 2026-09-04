# minidb-Ana-Samantha
minidb - Contrução de um SBD do zero em python, baseado em paginas de 4096 bytes e recuperação de falhas para a disciplina de Banco de Dados II.
O desevolvimento do SGBD será realizados em módulos
1. **M1 — Página e arquivo de dados:** Escrita e leitura física de blocos (páginas) de 4096 bytes em disco.
2. **M2 — Cache de páginas (Buffer Pool):** Páginas em memória, marcação de página suja, escrita no disco.
3. **M3 — Árvore B+:** Busca e inserção com divisão de nó.
4. **M4 — Parser e catálogo:** Tradutor de comandos SQL textuais para instruções que o motor entende.
5. **M5 — Executor:** Modelo iterador, varredura sequencial, varredura por índice e filtro..
6. **M6 — Transações:** Controle básico de transações (`BEGIN`, `COMMIT` e `ROLLBACK`).
7. **M7 — Recuperação:** Log de escrita antecipada, e refazer e desfazer na partida.
