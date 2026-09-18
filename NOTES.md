# M1
*17/09/2026
Realizamos a implementação das funções basicas necessárias para o módulo 1, com a implementação das seguintes funções:
`le_pagina(pager, n)`: Lê e retorna exatamente os 4096 bytes da página `n` no arquivo. Lança erro de leitura caso o bloco venha incompleto.
* `escreve_pagina(pager, n, buf)`: Valida se o buffer possui estritamente 4096 bytes e o grava na posição da página `n` no disco.
* `insere(pager, registro_bytes)`: Procura um slot livre nas páginas existentes, escreve o registro de 8 bytes, atualiza a contagem de slots no cabeçalho e retorna o RID `(página, slot)`. Aloca uma nova página caso as existentes estejam cheias.
* `deslocamento(pagina, slot)`: Calcula o byte absoluto do registro via fórmula `(página * 4096) + 16 + (slot * 8)`.
* `aloca()`: Expande o banco de dados gravando 4096 zeros binários (`b'\x00'`) ao final do arquivo e incrementa o totalizador de páginas.
* `sync()`: Combina `f.flush()` com `os.fsync(f.fileno())` para forçar a gravação física da memória RAM do sistema operacional no disco rígido.
