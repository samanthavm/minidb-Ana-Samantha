import sys
import os
import struct

TAMANHO_PAGINA = 4096
TAMANHO_CABECALHO = 16
TAMANHO_REGISTRO = 8

def le_pagina(nome_arquivo: str, n: int) -> bytearray:
    offset = n * TAMANHO_PAGINA

    if not os.path.exists(nome_arquivo):
        return bytearray(TAMANHO_PAGINA)

    with open(nome_arquivo, "rb") as arq:
        arq.seek(offset)
        conteudo = arq.read(TAMANHO_PAGINA)

        if len(conteudo) < TAMANHO_PAGINA:
            conteudo = conteudo.ljust(TAMANHO_PAGINA, b"\x00")

        return bytearray(conteudo)

def escrever_pagina(nome_arquivo: str, n: int, bytes_pagina: bytes) -> None:
    if len(bytes_pagina) != TAMANHO_PAGINA:
        raise ValueError(f"A página deve ter exatamente {TAMANHO_PAGINA} bytes.")

    offset = n * TAMANHO_PAGINA
    modo = "r+b" if os.path.exists(nome_arquivo) else "w+b"

    with open(nome_arquivo, modo) as arq:
        arq.seek(0, os.SEEK_END)
        tamanho_atual = arq.tell()

        if tamanho_atual < offset:
            arq.write(b"\x00" * (offset - tamanho_atual))
        arq.seek(offset)
        arq.write(bytes_pagina)

def main():
    arquivo = input("Arquivo:")
    if arquivo == "":
        print("Nenhum nome de arquivo inserido")
    else:
        pagina2 = le_pagina(arquivo, 2)
        registro = struct.pack(">II",1, 20254000)
        slot0 = TAMANHO_CABECALHO + (0*TAMANHO_REGISTRO)

        pagina2[slot0:slot0 + TAMANHO_REGISTRO] = registro
        struct.pack_into(">H", pagina2, 0, 1)
        escrever_pagina(arquivo, 2, bytes(pagina2))
        print("Registro gravado com sucesso")

if __name__ == "__main__":
    main()
