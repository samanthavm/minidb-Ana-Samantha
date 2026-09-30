import os
import struct

MAGIC_NUMBER = b"MINIDB01"
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
        self.inicializa_pagina_0()

    def valida(self, n:int)-> None:
        if n < 0 or n >= self.n_paginas:
          raise IndexError(f"Acesso inválido a página {n}.Total de páginas {self.nu_paginas}") #raise invocar uma exceção 
        """IndexError um erro na lógica de manipulação de dados """
    
    def le_paginas(self, n:int) -> bytearray: #bytearry é uma sequência mutável de inteiros entre 0 e 255 que serve para armazenar e modificar dados binários
      self.valida(n)
      self.f.seek(n * TAMANHO_PAGINA) 
      """O seek muda o cursosr e a conta n * TAMANHO_PAGINA calcula onde a página começa"""
      buf= self.f.read(TAMANHO_PAGINA)
      if len(buf) != TAMANHO_PAGINA:
        raise IOError (f"Página Truncada") #Erro na comunicação com modos de entrada e saída 
      return bytearray(buf) #bytearray transforma a sequência de bytes em uma sequência mutável de inteiros entre 0 e 255
    
    def escreve_pagina(self, n:int, buf: bytes) -> None:
      self.valida(n)
      if len(buf) != TAMANHO_PAGINA:
        raise IOError (F"Página com {len(buf)} bytes. A página deve ter {TAMANHO_PAGINA} bytes")
      self.f.seek(TAMANHO_PAGINA * n) 
      self.f.write(buf) # Escreve um sequência de bytes no arquivp físico, a partir da posição do cursor. 
    
    def aloca(self) -> int:
      n= self.n_paginas
      self.f.seek(TAMANHO_PAGINA)
      self.f.write(bytes(TAMANHO_PAGINA))
      """A função bytes() transforma o número inteiro que foi passado como argumento  em um objeto  preenchido por 0, no nosso caso vai ter 4096 zeros """
      """Agora o self.f.write vai gravar essa sequencia de zeros no arquivo sequência"""
      self.n_paginas += 1
      return n
    
    def sync(self):
      self.f.flush() # empurra os dados internos do buffer da RAM do python para a RAM do Sistema Operacioanal 
      os.fsync(self.f.fileno())
      # FORMATOS DE CABEÇALHO E PÁGINA O 

    def close (self) -> None:
      if not self.f.closed:
        self.sync()
        self.f.close()

# FORMATOS DE CABEÇALHO E PÁGINA O 
    def inicializa_pagina_0(self) -> None:
        """Página 0: Metadados (Magic Number, versão, tamanho da página)"""
        self.aloca()
        p0 = bytearray(TAMANHO_PAGINA)
        cabecalho = struct.pack(">8sHIII", MAGIC_NUMBER, 1, TAMANHO_PAGINA, 1, 1)
        p0[0 : len(cabecalho)] = cabecalho
        self.escreve_pagina(0, bytes(p0))

    def inicializa_pagina_dados(self, n: int) -> bytearray:
        """Formata o cabeçalho de 16 bytes em uma nova página de dados"""
        p = bytearray(TAMANHO_PAGINA)
        cabecalho = struct.pack(">HII6s", 0, TAMANHO_REGISTRO, n, b'\x00' * 8)
        p[0: TAMANHO_CABECALHO] = cabecalho
        self.escreve_pagina(n, bytes(p))
        return p

    def insere(self, registro_bytes: bytes) -> tuple[int, int]:
        """Insere um registro em uma página disponível"""
        if len(registro_bytes) != TAMANHO_REGISTRO:
            raise ValueError(f"Registro com {len(registro_bytes)} bytes. O registro deve ter {TAMANHO_REGISTRO} bytes.")
        
        max_slots = (TAMANHO_PAGINA - TAMANHO_CABECALHO) // TAMANHO_REGISTRO
        pagina_alvo = -1
        slot_alvo = -1

        for n in range(1, self.n_paginas):
            buf = self.le_paginas(n)
            n_slots, _, _ = struct.unpack(">HII", buf[0:10])

            if n_slots < max_slots:
                pagina_alvo = n
                slot_alvo = n_slots
                break

        # Se todas as páginas estiverem cheias, aloca uma nova página de dados
        if pagina_alvo == -1:
            pagina_alvo = self.aloca()
            buf = self.inicializa_pagina_dados(pagina_alvo)
            slot_alvo = 0
        else:
            buf = self.le_paginas(pagina_alvo)

        # Copia os bytes do registro para o slot calculado
        offset = TAMANHO_CABECALHO + (slot_alvo * TAMANHO_REGISTRO)
        buf[offset: offset + TAMANHO_REGISTRO] = registro_bytes
        
        # Atualiza a contagem de slots no cabeçalho
        struct.pack_into(">H", buf, 0, slot_alvo + 1)
        self.escreve_pagina(pagina_alvo, bytes(buf))
        self.sync()
        return (pagina_alvo, slot_alvo)

def serializar_registro(id_aluno: int, matricula: int) -> bytes:
      """Serializa um registro de aluno em bytes"""
      return struct.pack(">II", id_aluno, matricula)

def desserializar_registro(registro_bytes: bytes) -> tuple[int, int]:
      """Desserializa bytes em um registro de aluno"""
      return struct.unpack(">II", registro_bytes)




    


 
    




  
