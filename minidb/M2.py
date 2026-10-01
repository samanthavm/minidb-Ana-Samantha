from collections import OrderedDict
from M1 import Pager

class Cache:
    def __init__(self, pager, capacidade=16):
        self.pager, self.cap = pager, capacidade
        self.frames = {} 
        self.suja   = set() #indica as paginas que foram modificadas e que ainda precisam ser alteradas no disco tambem
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
            self.frames[n] = self.pager.le_paginas(n) #se ainda tiver espaço coloca a pagina no frame usando a função le_paginas
            self.uso[n] = True
        self.fixada[n] = self.fixada.get(n, 0) + 1
        return self.frames[n]
    
    def _expulsa(self):
        for n in list(self.uso):
            if self.fixada.get(n, 0) == 0:
                if n in self.suja:
                    self.pager.escreve_pagina(n, self.frames[n])
                    self.suja.discard(n)
                del self.frames[n], self.uso[n]
                return
        raise RuntimeError("todas as páginas estão fixadas")

    def solta(self, n, sujou=False): #função para marcar a pagina como não sendo usada
        if self.fixada.get(n, 0) <= 0: #verifica se pagina está fixada
            raise RuntimeError(f"Página {n} não está fixada")
        if sujou:
            self.suja.add(n)
        self.fixada[n] -= 1
    
    def descarrega(self):
        for n in list(self.suja):
            self.pager.escreve_pagina(n, self.frames[n])
        self.suja.clear()
        self.pager.sync()