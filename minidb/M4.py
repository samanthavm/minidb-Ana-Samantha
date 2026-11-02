import re
import struct
# Definição dos tipos de token a partir das expressões regulares
# As expressões regulares (REGEX)ler uma string de texto e divide em pequenos tokens

regex_tokens = re.compile(     # re.compile: Compila um padrão de expressão regular em um objeto expressão regula(quando o computador pega esse texto, entende a lógica dele, cria a ferramenta na memória);

    r"""
    (?P<ESPACO_BRANCO>\s+) |
    (?P<PALAV_CHAVE>SELECT|FROM|WHERE|AND|OR) |
    (?P<IDENTIFICADOR>[a-zA-Z_][a-zA-Z0-9_]*) |  # Os identificadores começam obrigatoriamente com uma letra ou sublinhado 
    (?P<NUMERO>\d+(\.\d+)?) | #serve para validar números inteiros e números decimais 
    (?P<STRING>'[^']*'|"[^"]*") |
    (?P<SIMBOLO>[,\*=<>!]|\S)
"""
re.VERBOSE | re.IGNORECASE 
)
# re.VERBOSE é responsável por tornar as regex mais legíveis e fáceis de docuumentar, por exemplo, igorando espaços em branco 
# re.IGNORECASE serve para garantir que a busca não faça diferenca entre letra minúscula e maiúscula 

def tokenize(query: str):

  
