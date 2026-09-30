import os
from minidb.M1 import Pager, escreve_pagina, le_pagina, insere, serializar_registro, deserializar_registro

# Apaga o banco de teste antigo se existir
if os.path.exists("teste.db"):
    os.remove("teste.db")

print("Iniciando teste do M1...")

# 1. Cria o pager e aloca duas paginas
pager = Pager("teste.db")
p1 = pager.aloca()
p2 = pager.aloca()

# 2. Testa insere()
reg = serializar_registro(1, 20260001)
pag, slot = insere(pager, reg)
print(f"Registro inserido na pagina {pag}, slot {slot}")

# Fecha pra forcar a gravacao no disco
pager.close()

# 3. Reabre pra provar que gravou no disco de verdade
pager_reaberto = Pager("teste.db")

# Le a pagina onde o registro foi salvo
buf = le_pagina(pager_reaberto, pag)

# O primeiro registro fica logo apos o cabecalho de 16 bytes (offset 16)
dados_slot0 = buf[16:24]
id_aluno, mat = deserializar_registro(dados_slot0)

print(f"Lido do disco -> ID: {id_aluno}, Matricula: {mat}")
