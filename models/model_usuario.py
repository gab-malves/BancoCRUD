"""
model_usuario.py
Responsabilidade: Pessoa 3 - Back-end A

Modelo de dados genérico que representa um Usuário do sistema.
"""

class Usuario:
    """
    Representa um usuário no sistema logado em memória.

    Atributos:
        id (int): Identificador único do banco de dados gerado pela Pessoa 4 automagicamente.
        nome (str): Nome do cliente/usuário.
        cpf (str): CPF sem formatação, utilizado única e exclusivamente como identificador secundário lógico.
    """

    def __init__(self, id: int, nome: str, cpf: str):
        self.id = id
        self.nome = nome
        self.cpf = cpf

    def __str__(self) -> str:
        return f"Usuário: {self.nome} | CPF: {self.cpf}"

    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, nome={self.nome!r}, cpf={self.cpf!r})"
