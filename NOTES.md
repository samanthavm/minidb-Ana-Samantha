# M1
*17/09/2026
Realizamos a implementação das funções basicas necessárias para o módulo 1, com a implementação das seguintes funções:
`le_pagina(pager, n)`: Lê e retorna exatamente os 4096 bytes da página `n` no arquivo. Lança erro de leitura caso o bloco venha incompleto.
* `escreve_pagina(pager, n, buf)`: Valida se o buffer possui estritamente 4096 bytes e o grava na posição da página `n` no disco.
* `insere(pager, registro_bytes)`: Procura um slot livre nas páginas existentes, escreve o registro de 8 bytes, atualiza a contagem de slots no cabeçalho e retorna o RID `(página, slot)`. Aloca uma nova página caso as existentes estejam cheias.
* `deslocamento(pagina, slot)`: Calcula o byte absoluto do registro via fórmula `(página * 4096) + 16 + (slot * 8)`.
* `aloca()`: Expande o banco de dados gravando 4096 zeros binários (`b'\x00'`) ao final do arquivo e incrementa o totalizador de páginas.
* `sync()`: Combina `f.flush()` com `os.fsync(f.fileno())` para forçar a gravação física da memória RAM do sistema operacional no disco rígido.

# M3
Cada nó da árvore B+ ocupa uma página de 4096 bytes do arquivo de índice, gravada com `struct` em big-endian, como no M1. A página começa com um cabeçalho de 3 bytes, igual nos dois tipos de nó, com os cmpos`eh_folha` (`B`, 1 byte) e `quant`, o número de chaves (`H`, 2 bytes).
O `eh_folha` permite saber como interpretar o resto da página. Na folha, logo após o cabeçalho vem o `pont_prox` (`i`, 4 bytes, com sinal para aceitar o `-1` de "não há próxima folha"), seguido de `quant` entradas de 10 bytes, cada uma com a chave (`I`), a página do registro (`I`) e o slot (`H`) no arquivo de dados do M1.
No nó interno, após o cabeçalho vêm as `quant` chaves separadoras (`I`, 4 bytes cada) e depois `quant + 1` números de página dos filhos (`I`, 4 bytes cada), um filho a mais que chaves porque `n` separadores criam `n + 1` intervalos de busca; ele não tem `pont_prox`, já que o encadeamento existe só entre folhas. O restante da página é preenchido com zeros, e o `quant` indica até onde ler.
