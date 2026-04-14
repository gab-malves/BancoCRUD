"""
conta_controller.py
Responsabilidade: Pessoa 4 - Back-end B & Banco de Dados

Controller responsável pelas operações relacionadas a Contas Bancárias.
Faz a ponte entre a camada de Views (telas) e a camada de dados (BancoDados).
Toda lógica de criação, consulta e exclusão de contas passa por aqui.
"""

from database.banco_sqlite import BancoDados
from models.model_conta import Conta


class ContaController:
    """
    Gerencia as operações de conta bancária:
    - Criação de novas contas
    - Consulta de conta e saldo
    - Listagem de todas as contas
    - Exclusão de conta
    """

    def __init__(self):
        self.db = BancoDados()

    # ------------------------------------------------------------------
    # Criar conta
    # ------------------------------------------------------------------

    def criar_conta(self, numero: str, titular: str, saldo_inicial: float = 0.0) -> dict:
        """
        Cria e persiste uma nova conta bancária.

        Retorna um dicionário com:
            sucesso  (bool): True se criada com sucesso
            mensagem (str):  Mensagem informativa
            conta    (Conta | None): Objeto criado
        """
        numero  = numero.strip()
        titular = titular.strip()

        if not numero or not titular:
            return {"sucesso": False, "mensagem": "Número e titular são obrigatórios.", "conta": None}

        if saldo_inicial < 0:
            return {"sucesso": False, "mensagem": "Saldo inicial não pode ser negativo.", "conta": None}

        nova_conta = Conta(numero, titular, saldo_inicial)
        criada = self.db.salvar_conta(nova_conta)

        if criada:
            return {"sucesso": True, "mensagem": f"Conta {numero} criada com sucesso!", "conta": nova_conta}
        else:
            return {"sucesso": False, "mensagem": f"Já existe uma conta com o número '{numero}'.", "conta": None}

    # ------------------------------------------------------------------
    # Consultar conta e saldo
    # ------------------------------------------------------------------

    def consultar_conta(self, numero: str) -> dict:
        """
        Busca uma conta pelo número e retorna seus dados atualizados.

        Retorna um dicionário com:
            sucesso  (bool)
            mensagem (str)
            conta    (Conta | None)
        """
        conta = self.db.buscar_conta(numero.strip())

        if conta:
            return {"sucesso": True, "mensagem": str(conta), "conta": conta}
        return {"sucesso": False, "mensagem": f"Conta '{numero}' não encontrada.", "conta": None}

    def consultar_saldo(self, numero: str) -> dict:
        """
        Retorna o saldo atual de uma conta.

        Retorna um dicionário com:
            sucesso  (bool)
            mensagem (str)
            saldo    (float | None)
        """
        resultado = self.consultar_conta(numero)
        if resultado["sucesso"]:
            saldo = resultado["conta"].saldo
            return {
                "sucesso": True,
                "mensagem": f"Saldo disponível: R$ {saldo:,.2f}",
                "saldo": saldo
            }
        return {"sucesso": False, "mensagem": resultado["mensagem"], "saldo": None}

    # ------------------------------------------------------------------
    # Listar contas
    # ------------------------------------------------------------------

    def listar_contas(self) -> list[Conta]:
        """
        Retorna a lista de todas as contas cadastradas no sistema.
        """
        return self.db.listar_contas()

    # ------------------------------------------------------------------
    # Excluir conta
    # ------------------------------------------------------------------

    def excluir_conta(self, numero: str) -> dict:
        """
        Remove uma conta do banco de dados.

        Retorna um dicionário com:
            sucesso  (bool)
            mensagem (str)
        """
        removida = self.db.excluir_conta(numero.strip())

        if removida:
            return {"sucesso": True, "mensagem": f"Conta '{numero}' removida com sucesso."}
        return {"sucesso": False, "mensagem": f"Conta '{numero}' não encontrada para exclusão."}
