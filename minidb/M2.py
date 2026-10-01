from collections import OrderedDict
from M1 import Pager
class Cache:
    def __init__(self, pager, capacidade=16):
        self.pager, self.cap = pager, capacidade
        self.frames = {} 
        self.suja   = set()
        self.fixada = {} 
        self.uso    = OrderedDict()
        self.acertos = self.faltas = 0

    def fixa(self, n):
        if n in self.frames:
            self.acertos += 1 
            self.uso.move_to_end(n)
        else: #a pagina não esta no cache
            self.faltas += 1 
            if len(self.frames) == self.cap: #verifica se tem espaço
                self._expulsa() 
            self.frames[n] = self.pager.le_paginas(n) #se ainda tiver espaço coloca a pagina no frame usando a função le pagina
            self.uso[n] = True
        self.fixada[n] = self.fixada.get(n, 0) + 1
        return self.frames[n]