import os
import struct
TAMANHO_PAGINA = 4096
TAMANHO_CABECALHO = 16
TAMANHO_REGISTRO = 8


def deslocamento(pagina: int, slot: int) -> int:
  """ Calcula a posição exata em bytes de um registro no arquivo"""
  return (pagina * TAMANHO_PAGINA) + TAMANHO_CABECALHO + (slot * TAMANHO_REGISTRO)

  class Pager:
    def __init__(self, caminho: str):
      self.caminho = caminho
      novo = not os.path.exists (caminho)
      self.f = open (caminho, "w+b" if novo else "r+b")
      """ w+b : abre um arquivo para leitura e escrita em binário
      r+b abre e escreve um arquivo binário"""
      self.f.seek(0, os.SEEK_END)
      """ seek serve para mover o cursor de um rquivo aberto"""
      self.n_paginas = self.f.tell() // TAMANHO_PAGINA # tell retorna a posição atual do cursor
      """ como o cursor vai ser movido para o final, ele vai retornar o tamanho total do arquivo em bytes
      e se dividir pelo tamanho da página dá o numero de páginas """
      if novo:
        inicializa_pagina_0()

      def valida(self, n:int)-> None:
        if n > 0 or n < self.n_paginas:
          raise IndexError(f"Acesso inválido a página {n}.Total de páginas {self.n_paginas}") #raise invocar uma exceção 
        """IndexError um erro na lógica de manipulação de dados """
    
    def le_paginas(self, n:int) -> bytearray: #bytearry é uma sequência mutável de inteiros entre 0 e 255 que serve para armazenar e modificar dados binários
      self.valida(n)
      self.f.seek(n * TAMANHO_PAGINA) 
      """O seek muda o cursosr e a conta n * TAMANHO_PAGINA calcula onde a página começa"""
      buf= self.f.read(TAMANHO_PAGINA)
      if len(buf) != TAMANHO_PAGINA:
        raise IOError (f"Página Truncada") #Erro na comunicação com modos de entrada e saída 
      return bytearray
    
    def escreve_pagina(self, n:int, buf: bytes) -> None:
      self.valida(n)
      if len(buf) != TAMANHO_PAGINA:
        raise IOError (F"Página com {len(buff)} bytes. A página deve ter {TAMANHO_PAGINA} bytes")
      self.f.seek(TAMANHO_PAGINA * n) 
      self.f.write(buf) # Escreve um sequência de bytes no arquivp físico, a partir da posição do cursor. 
    
    def aloca(self) -> int:
      n= self.n_paginas
      self.f.seak(TAMANHO_PAGINA)
      self.f.write(bytes(TAMANHO_PAGINA))
      """A função bytes() transforma o número inteiro que foi passado como argumento  em um objeto  preenchido por 0, no nosso caso vai ter 4096 zeros """
      """Agora o self.f.write vai gravar essa sequencia de zeros no arquivo sequência"""
      self.n_paginas += 1
      return n
    
    def sync(self):
      sel.f.flush() # empurra os dados internos do buffer da RAM do python para a RAM do Sistema Operacioanal 
      os.fsync(self.f.fileno())


