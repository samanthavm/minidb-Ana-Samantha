import re
import struct

# Definição dos tipos de token a partir das expressões regulares
# As expressões regulares (REGEX) lêem uma string de texto e dividem-na em pequenos tokens
REGEX_TOKENS = re.compile(
    r"""
    (?P<ESPACO_BRANCO>\s+) |
    (?P<PALAV_CHAVE>SELECT|FROM|WHERE|AND|OR) |
    (?P<IDENTIFICADOR>[a-zA-Z_][a-zA-Z0-9_]*) |  # Os identificadores começam obrigatoriamente com uma letra ou sublinhado
    (?P<NUMERO>\d+(\.\d+)?) | # Serve para validar números inteiros e números decimais
    (?P<STRING>'[^']*'|"[^"]*") |
    (?P<SIMBOLO>[,\*=<>!]|\S)
    """,
    re.VERBOSE | re.IGNORECASE
)

# re.VERBOSE é responsável por tornar as regex mais legíveis e fáceis de documentar, por exemplo, ignorando espaços em branco
# re.IGNORECASE serve para garantir que a busca não faça diferença entre letra minúscula e maiúscula

def tokenize(consulta: str):
    tokens = []
    for encontrado in REGEX_TOKENS.finditer(consulta.strip()):
        # consulta.strip() remove espaços em branco, tabulações que estejam no início e no fim de uma string
        # finditer é um método que procura correspondências da expressão regular ao longo do código e retorna um iterador
        tipo = encontrado.lastgroup
        valor = encontrado.group(tipo)
        
        if tipo == 'ESPACO_BRANCO':
            continue
        if tipo == 'PALAV_CHAVE':
            valor = valor.upper()
        tokens.append((tipo, valor))
    return tokens


class SelectParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0

    def _atual(self):
        if self.posicao < len(self.tokens):
            return self.tokens[self.posicao]
        return (None, None)

    def _consumir(self, esperado_tipo=None, esperado_valor=None):
        tipo, valor = self._atual()
        if tipo is None: # Verifica se a consulta SQL terminou antes do tempo
            raise SyntaxError("Fim inesperado da Consulta!")
        if esperado_tipo and tipo != esperado_tipo: # Valida se a categoria/tipo do token atual é exatamente a que o parser espera naquele momento
            raise SyntaxError(f"Esperado tipo {esperado_tipo}, obtido {tipo} ({valor})")
        if esperado_valor and valor.upper() != esperado_valor.upper(): # Valida se o conteúdo exato do token corresponde ao esperado
            raise SyntaxError(f"Esperado '{esperado_valor}', obtido '{valor}'")
        self.posicao += 1
        return valor

    def parse(self):
        # Espera 'SELECT' (Exige que o 1º token seja a palavra select)
        self._consumir('PALAV_CHAVE', 'SELECT')

        # Extrai as colunas (Verifica se pediu as colunas usando * )
        colunas = []
        if self._atual() == ('SIMBOLO', '*'): # vê se o token atual é o asterisco, se for chama a função consumir e guarda o elemento '*'
            self._consumir('SIMBOLO', '*')
            colunas = ['*']
        else:
            # Se não houver o asterisco, entra no bloco else e pede obrigatoriamente um identificador, já que se escolhem por nome as colunas para consulta
            while True:
                colunas.append(self._consumir('IDENTIFICADOR'))
                if self._atual() == ('SIMBOLO', ','):
                    self._consumir('SIMBOLO', ',')
                else:
                    break

        # Espera 'FROM'
        self._consumir('PALAV_CHAVE', 'FROM')

        # Extrai Nome da Tabela
        tabela = self._consumir('IDENTIFICADOR')

        condicao = None
        # A variável condição é criada, mas é definida como vazia porque o uso de Where é opcional
        tipo, valor = self._atual()
        if tipo == 'PALAV_CHAVE' and valor == 'WHERE':
            self._consumir('PALAV_CHAVE', 'WHERE')
            colu_cond = self._consumir('IDENTIFICADOR') # consome a coluna do filtro
            operador = self._consumir('SIMBOLO') # consome operador da comparação, ex: =, <
            valor_cond = self._consumir() # consome valor a comparar
            condicao = (colu_cond, operador, valor_cond[1]) # Junta estes três elementos num tuplo limpo (coluna, operador, valor)

        return {
            "tipo": "SELECT",
            "colunas": colunas,
            "tabela": tabela,
            "condicao": condicao
        }
