"""
validacoes.py
Funções utilitárias gerais para validação e formatação de dados.
"""
import re

def limpar_cpf(cpf: str) -> str:
    """
    Remove pontuações do CPF deixando apenas os números.
    Essa sanitização é necessária para manter a tabela limpa e fácilita a verificação de duplicidade.
    """
    return re.sub(r'\D', '', cpf)

def formatar_cpf(cpf: str) -> str:
    """
    Aplica uma formatação simples no CPF (XXX.XXX.XXX-XX) caso tenha 11 dígitos, ignorando qualquer outra.
    """
    cpf_limpo = limpar_cpf(cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf_limpo
