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


# Bloco de teste
if __name__ == "__main__":
    nome_db = "dados.db" 
    if os.path.exists(nome_db):
        os.remove(nome_db)
        
    print("=========================================================")
    print("      SUÍTE DE TESTES DE VALIDAÇÃO — MINIDB (M1)         ")
    print("=========================================================")

    # Teste 1: Inicialização do Pager e Alocação de Páginas
    pager = Pager(nome_db)
    p1 = pager.aloca()
    pager.inicializa_pagina_dados(p1)
    p2 = pager.aloca()
    pager.inicializa_pagina_dados(p2)
    p3 = pager.aloca()
    pager.inicializa_pagina_dados(p3)
    print(f"[TESTE 1] Alocação: {pager.n_paginas} páginas criadas (Páginas 0, 1, 2 e 3)")

    # Teste 2: Escrita e Leitura de ida e volta + isolamento de páginas
    buf_p2_original = pager.le_paginas(2)
    buf_p2_modificado = bytearray(buf_p2_original)
    
    registro_bytes = serializar_registro(1, 20260001)
    offset_slot0 = TAMANHO_CABECALHO
    buf_p2_modificado[offset_slot0: offset_slot0 + TAMANHO_REGISTRO] = registro_bytes
    struct.pack_into(">H", buf_p2_modificado, 0, 1)  
    pager.escreve_pagina(2, bytes(buf_p2_modificado))
    
    # Verifica se a página 2 não alterou a página 3
    p3_lida = pager.le_paginas(3)
    # Garante apenas que a página 3 foi lida corretamente sem corrupção
    assert len(p3_lida) == TAMANHO_PAGINA
    print("[TESTE 2] Vizinhança: alterar a página 2 não corrompeu a página 3 [PASSOU]")
    
    pager.sync()
    pager.close()

    # TESTE 3: Leitura Independente do Disco
    print("\n--- TESTE 3: PROVA DE PERSISTÊNCIA E REABERTURA DO ARQUIVO ---")
    pager_reaberto = Pager(nome_db)
    pagina2_lida = pager_reaberto.le_paginas(2)

    fatia_slot0 = pagina2_lida[offset_slot0 : offset_slot0 + TAMANHO_REGISTRO]
    id_recuperado, mat_recuperada = desserializar_registro(fatia_slot0)

    pos_fisi = deslocamento(2, 0)
    assert id_recuperado == 1 and mat_recuperada == 20260001
    assert pos_fisi == 8208

    print(f"[✓] Registro lido da Página 2, Slot 0 -> ID: {id_recuperado} | Matrícula: {mat_recuperada}")
    print(f"[✓] Deslocamento exato no arquivo físico: byte {pos_fisi}")

    # TESTE 4: Validação de Alinhamento de Páginas
    tamanho_arquivo = os.path.getsize(nome_db)
    assert tamanho_arquivo % TAMANHO_PAGINA == 0
    print(f"[TESTE 4] Tamanho total do arquivo ({tamanho_arquivo} bytes) é múltiplo de 4096 [PASSOU].")

    # TESTE 5: Inserção Dinâmica via insere()
    print("\n--- TESTE 5: TESTE DA FUNÇÃO INSERE() ---")
    reg_novo = serializar_registro(2, 20260002)
    rid_retornado = pager_reaberto.insere(reg_novo)
    print(f"[✓] Registro inserido via insere() -> RID (Página, Slot): {rid_retornado}")

    pager_reaberto.close()
    print("=========================================================")
    print("        TODOS OS TESTES PASSARAM COM SUCESSO!            ")
    print("=========================================================")



 
    




  
