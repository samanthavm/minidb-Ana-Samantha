import struct
from bisect import bisect_left, bisect_right

from M1 import Pager, TAMANHO_PAGINA
from M2 import Cache

# Cabeçalho comum
FMT_CAB = ">BH"
TAM_CAB = struct.calcsize(FMT_CAB)
# Folha
FMT_PROX = ">i"
TAM_PROX = struct.calcsize(FMT_PROX)
FMT_ENTRADA_FOLHA = ">IIH"
TAM_ENTRADA_FOLHA = struct.calcsize(FMT_ENTRADA_FOLHA)
# Nó interno
TAM_CHAVE = 4
TAM_FILHO = 4

CAP_FOLHA = (TAMANHO_PAGINA - TAM_CAB - TAM_PROX) // TAM_ENTRADA_FOLHA
CAP_INTERNO = (TAMANHO_PAGINA - TAM_CAB - TAM_FILHO) // (TAM_CHAVE + TAM_FILHO)
CAPACIDADE_FISICA = min(CAP_FOLHA, CAP_INTERNO)

MAX_CHAVES = 3
OFFSET_RAIZ = 64 #posição do número da raiz na página 0 do índice
SEM_PROXIMA = -1


class No:
    def __init__(self, pagina, eh_folha=False):
        self.pagina = pagina
        self.eh_folha = eh_folha
        self.chaves = []
        self.quant = 0
        self.filhos = []
        self.registros = [] #(pagina, slot)
        self.pont_prox = SEM_PROXIMA

    def serializar(self) -> bytes:
        self.quant = len(self.chaves)
        buf = bytearray(TAMANHO_PAGINA)
        struct.pack_into(FMT_CAB, buf, 0, 1 if self.eh_folha else 0, self.quant)
        off = TAM_CAB
        if self.eh_folha:
            if len(self.registros) != self.quant:
                raise ValueError("folha com chaves e registros em número diferente")
            struct.pack_into(FMT_PROX, buf, off, self.pont_prox)
            off += TAM_PROX
            for c, (pg, sl) in zip(self.chaves, self.registros):
                struct.pack_into(FMT_ENTRADA_FOLHA, buf, off, c, pg, sl)
                off += TAM_ENTRADA_FOLHA
        else:
            if len(self.filhos) != self.quant + 1:
                raise ValueError("nó interno deve ter quant + 1 filhos")
            for c in self.chaves:
                struct.pack_into(">I", buf, off, c)
                off += TAM_CHAVE
            for f in self.filhos:
                struct.pack_into(">I", buf, off, f)
                off += TAM_FILHO
        assert len(buf) == TAMANHO_PAGINA
        return bytes(buf)

    @classmethod
    def desserializar(cls, pagina, buf) -> "No":
        eh_folha, quant = struct.unpack_from(FMT_CAB, buf, 0)
        no = cls(pagina, bool(eh_folha))
        no.quant = quant
        off = TAM_CAB
        if no.eh_folha:
            (no.pont_prox,) = struct.unpack_from(FMT_PROX, buf, off)
            off += TAM_PROX
            for _ in range(quant):
                c, pg, sl = struct.unpack_from(FMT_ENTRADA_FOLHA, buf, off)
                no.chaves.append(c)
                no.registros.append((pg, sl))
                off += TAM_ENTRADA_FOLHA
        else:
            for _ in range(quant):
                (c,) = struct.unpack_from(">I", buf, off)
                no.chaves.append(c)
                off += TAM_CHAVE
            for _ in range(quant + 1):
                (f,) = struct.unpack_from(">I", buf, off)
                no.filhos.append(f)
                off += TAM_FILHO
        return no


class ArvoreBMais:
    def __init__(self, caminho_indice, max_chaves=MAX_CHAVES, capacidade_cache=16):
        if not (2 <= max_chaves <= CAPACIDADE_FISICA):
            raise ValueError(f"max_chaves deve estar entre 2 e {CAPACIDADE_FISICA}")
        self.max_chaves = max_chaves
        self.pager = Pager(caminho_indice)
        self.cache = Cache(self.pager, capacidade_cache)
        self.leituras = 0 # nós lidos (para conferir "páginas lidas = altura")

        if self.pager.n_paginas == 1:       # índice novo: cria a raiz (folha vazia)
            raiz = self._novo_no(eh_folha=True)
            self._grava(raiz)
            self._set_raiz(raiz.pagina)
        self.raiz = self._get_raiz()

    # ----------acesso a páginas via cache----------
    def _le(self, n) -> No:
        frame = self.cache.fixa(n)
        try:
            no = No.desserializar(n, frame)
        finally:
            self.cache.solta(n)
        self.leituras += 1
        return no

    def _grava(self, no: No) -> None:
        frame = self.cache.fixa(no.pagina)
        frame[:] = no.serializar()          # copia para dentro do frame
        self.cache.solta(no.pagina, sujou=True)

    def _novo_no(self, eh_folha) -> No:
        return No(self.pager.aloca(), eh_folha)

    def _get_raiz(self) -> int:
        frame = self.cache.fixa(0)
        try:
            (r,) = struct.unpack_from(">i", frame, OFFSET_RAIZ)
        finally:
            self.cache.solta(0)
        return r

    def _set_raiz(self, n) -> None:
        frame = self.cache.fixa(0)
        struct.pack_into(">i", frame, OFFSET_RAIZ, n)
        self.cache.solta(0, sujou=True)
        self.raiz = n

    # ----------busca----------
    def _descer(self, chave):
        """Desce da raiz até a folha. Retorna (folha, caminho_de_nos_internos)."""
        caminho = []
        no = self._le(self.raiz)
        while not no.eh_folha:
            caminho.append(no)
            i = bisect_right(no.chaves, chave)   # chave == separador vai para a direita
            no = self._le(no.filhos[i])
        return no, caminho

    def buscar(self, chave):
        """Retorna (pagina, slot) do registro, ou None."""
        folha, _ = self._descer(chave)
        i = bisect_left(folha.chaves, chave)
        if i < len(folha.chaves) and folha.chaves[i] == chave:
            return folha.registros[i]
        return None

    def buscar_intervalo(self, inicio, fim):
        """Gera (chave, (pagina, slot)) com inicio <= chave <= fim, seguindo as folhas."""
        folha, _ = self._descer(inicio)
        while True:
            for c, r in zip(folha.chaves, folha.registros):
                if c > fim:
                    return
                if c >= inicio:
                    yield c, r
            if folha.pont_prox == SEM_PROXIMA:
                return
            folha = self._le(folha.pont_prox)

    def altura(self) -> int:
        h, no = 1, self._le(self.raiz)
        while not no.eh_folha:
            no = self._le(no.filhos[0])
            h += 1
        return h

    # ---------- inserção ----------
    def inserir(self, chave, pagina, slot) -> None:
        folha, caminho = self._descer(chave)
        i = bisect_left(folha.chaves, chave)
        if i < len(folha.chaves) and folha.chaves[i] == chave:
            raise ValueError(f"chave {chave} já existe")
        folha.chaves.insert(i, chave)
        folha.registros.insert(i, (pagina, slot))

        if len(folha.chaves) <= self.max_chaves:
            self._grava(folha)
            return

        # divisão da folha: a chave do meio é COPIADA para o pai
        meio = len(folha.chaves) // 2
        nova = self._novo_no(eh_folha=True)
        nova.chaves = folha.chaves[meio:]
        nova.registros = folha.registros[meio:]
        nova.pont_prox = folha.pont_prox        # 1º: a nova herda o próximo
        folha.chaves = folha.chaves[:meio]
        folha.registros = folha.registros[:meio]
        folha.pont_prox = nova.pagina           # 2º: só então a original aponta para a nova
        self._grava(folha)
        self._grava(nova)

        sobe, filho_novo, esquerdo = nova.chaves[0], nova.pagina, folha

        # propaga para os pais
        while True:
            if not caminho:                     # dividiu a raiz: nasce uma raiz nova
                raiz = self._novo_no(eh_folha=False)
                raiz.chaves = [sobe]
                raiz.filhos = [esquerdo.pagina, filho_novo]
                self._grava(raiz)
                self._set_raiz(raiz.pagina)
                return
            pai = caminho.pop()
            j = bisect_right(pai.chaves, sobe)
            pai.chaves.insert(j, sobe)
            pai.filhos.insert(j + 1, filho_novo)
            if len(pai.chaves) <= self.max_chaves:
                self._grava(pai)
                return
            # divisão de nó interno: a chave do meio sobe
            meio = len(pai.chaves) // 2
            sobe = pai.chaves[meio]
            novo = self._novo_no(eh_folha=False)
            novo.chaves = pai.chaves[meio + 1:]
            novo.filhos = pai.filhos[meio + 1:]
            pai.chaves = pai.chaves[:meio]
            pai.filhos = pai.filhos[:meio + 1]
            self._grava(pai)
            self._grava(novo)
            filho_novo, esquerdo = novo.pagina, pai

    # ----------ciclo de vida----------
    def fechar(self) -> None:
        self.cache.descarrega()
        self.pager.close()