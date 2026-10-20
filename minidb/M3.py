import struct

from M1 import Pager
from M2 import Cache


TAMANHO_PAGINA = 4096
MAX_CHAVES = 3


class No:
    def __init__(self, pagina):
        self.pagina = pagina
        self.chaves = []
        self.quant = 0
        self.filhos = [] #número da pagina dos nós filhos 
        self.registros = []
        self.pont_prox = None #numero da proxima pagina 