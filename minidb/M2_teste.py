import os

from M1 import Pager, TAMANHO_PAGINA
from M2 import Cache

def cria_pager_com_paginas(caminho, quantidade):
    pager = Pager(caminho)

    while pager.n_paginas < quantidade:
        n = pager.aloca()
        pager.inicializa_pagina_dados(n)

    return pager

def test_acerto():
    caminho = "teste_acerto.db"

    pager = cria_pager_com_paginas(caminho, 2)
    cache = Cache(pager, capacidade=3)

    cache.fixa(1)
    cache.solta(1)

    cache.fixa(1)
    cache.solta(1)

    assert cache.faltas == 1
    assert cache.acertos == 1

    cache.descarrega()
    pager.close()

    os.remove(caminho)

def test_explusao():
    caminho = "teste_expulsao.db"

    pager = cria_pager_com_paginas(caminho, 5)
    cache = Cache(pager, capacidade=3)

    cache.fixa(1)
    cache.solta(1)

    cache.fixa(2)
    cache.solta(2)

    cache.fixa(3)
    cache.solta(3)

    cache.fixa(4)
    cache.solta(4)

    assert 1 not in cache.frames
    assert 2 in cache.frames
    assert 3 in cache.frames
    assert 4 in cache.frames

    cache.descarrega()
    pager.close()

    os.remove(caminho)

def test_pagina_suja():
    caminho = "teste_suja.db"
    
    pager = cria_pager_com_paginas(caminho, 5)
    cache = Cache(pager, capacidade=3)

    pagina = cache.fixa(1)

    pagina[100] = 123

    cache.solta(1, sujou=True)

    cache.fixa(2)
    cache.solta(2)

    cache.fixa(3)
    cache.solta(3)

    cache.fixa(4)
    cache.solta(4)

    assert 1 not in cache.frames

    cache.descarrega()
    pager.close()

    pager2 = Pager(caminho)
    cache2 = Cache(pager2, capacidade=3)

    pagina = cache2.fixa(1)

    assert pagina[100] == 123

    cache2.solta(1)
    cache2.descarrega()
    pager2.close()

    os.remove(caminho)
