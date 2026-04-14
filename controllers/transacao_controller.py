"""
transacao_controller.py
Responsabilidade: Pessoa 4 - Back-end B & Banco de Dados

Controller responsável por todas as operações financeiras:
Depósito, Saque, Transferência e PIX.

Aqui ficam todas as regras de negócio matemáticas e de validação
antes de qualquer movimentação ser persistida no banco.
"""

from database.banco_sqlite import BancoDados
from models.model_conta import Conta
from models.model_transacao import Transacao


class TransacaoController:
    """
    Gerencia operações financeiras entre contas:
    - Depósito
    - Saque
    - Transferência (entre contas internas)
    - PIX
    - Consulta de extrato
    """

    def __init__(self):
        self.db = BancoDados()

    # ------------------------------------------------------------------
    # Método interno de validação de valor
    # ------------------------------------------------------------------

    def _validar_valor(self, valor) -> dict | None:
        """
        Tenta converter e validar o valor monetário informado.
        Retorna None se válido, ou um dict de erro se inválido.
        """
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return {"sucesso": False, "mensagem": "Valor inválido. Informe um número."}

        if valor <= 0:
            return {"sucesso": False, "mensagem": "O valor deve ser maior que zero."}

        return None  # sem erros

    # ------------------------------------------------------------------
    # Depósito
    # ------------------------------------------------------------------

    def depositar(self, numero_conta: str, valor) -> dict:
        """
        Realiza um depósito na conta informada.

        Retorna:
            sucesso  (bool)
            mensagem (str)
            saldo    (float | None): Novo saldo após o depósito
        """
        erro = self._validar_valor(valor)
        if erro:
            return erro

        valor = float(valor)
        conta = self.db.buscar_conta(numero_conta.strip())

        if not conta:
            return {"sucesso": False, "mensagem": f"Conta '{numero_conta}' não encontrada.", "saldo": None}

        conta.depositar(valor)
        self.db.atualizar_saldo(conta)

        transacao = Transacao(conta_origem=conta.numero, tipo="DEPOSITO", valor=valor)
        self.db.registrar_transacao(transacao)

        return {
            "sucesso":  True,
            "mensagem": f"Depósito de R$ {valor:,.2f} realizado com sucesso!",
            "saldo":    conta.saldo
        }

    # ------------------------------------------------------------------
    # Saque
    # ------------------------------------------------------------------

    def sacar(self, numero_conta: str, valor) -> dict:
        """
        Realiza um saque na conta informada com validação de saldo.

        Retorna:
            sucesso  (bool)
            mensagem (str)
            saldo    (float | None): Novo saldo após o saque
        """
        erro = self._validar_valor(valor)
        if erro:
            return erro

        valor = float(valor)
        conta = self.db.buscar_conta(numero_conta.strip())

        if not conta:
            return {"sucesso": False, "mensagem": f"Conta '{numero_conta}' não encontrada.", "saldo": None}

        if not conta.sacar(valor):
            return {
                "sucesso":  False,
                "mensagem": f"Saldo insuficiente. Saldo atual: R$ {conta.saldo:,.2f}",
                "saldo":    conta.saldo
            }

        self.db.atualizar_saldo(conta)

        transacao = Transacao(conta_origem=conta.numero, tipo="SAQUE", valor=valor)
        self.db.registrar_transacao(transacao)

        return {
            "sucesso":  True,
            "mensagem": f"Saque de R$ {valor:,.2f} realizado com sucesso!",
            "saldo":    conta.saldo
        }

    # ------------------------------------------------------------------
    # Transferência
    # ------------------------------------------------------------------

    def transferir(self, numero_origem: str, numero_destino: str, valor) -> dict:
        """
        Realiza uma transferência entre duas contas internas.

        Retorna:
            sucesso         (bool)
            mensagem        (str)
            saldo_origem    (float | None): Saldo atualizado da conta de origem
        """
        erro = self._validar_valor(valor)
        if erro:
            return erro

        valor          = float(valor)
        numero_origem  = numero_origem.strip()
        numero_destino = numero_destino.strip()

        if numero_origem == numero_destino:
            return {"sucesso": False, "mensagem": "Origem e destino não podem ser a mesma conta.", "saldo_origem": None}

        conta_origem  = self.db.buscar_conta(numero_origem)
        conta_destino = self.db.buscar_conta(numero_destino)

        if not conta_origem:
            return {"sucesso": False, "mensagem": f"Conta de origem '{numero_origem}' não encontrada.", "saldo_origem": None}

        if not conta_destino:
            return {"sucesso": False, "mensagem": f"Conta de destino '{numero_destino}' não encontrada.", "saldo_origem": None}

        if not conta_origem.transferir_para(conta_destino, valor):
            return {
                "sucesso":      False,
                "mensagem":     f"Saldo insuficiente. Saldo atual: R$ {conta_origem.saldo:,.2f}",
                "saldo_origem": conta_origem.saldo
            }

        # Persiste os dois saldos atualizados
        self.db.atualizar_saldo(conta_origem)
        self.db.atualizar_saldo(conta_destino)

        transacao = Transacao(
            conta_origem=numero_origem,
            conta_destino=numero_destino,
            tipo="TRANSFERENCIA",
            valor=valor
        )
        self.db.registrar_transacao(transacao)

        return {
            "sucesso":      True,
            "mensagem":     f"Transferência de R$ {valor:,.2f} para a conta {numero_destino} realizada!",
            "saldo_origem": conta_origem.saldo
        }

    # ------------------------------------------------------------------
    # PIX
    # ------------------------------------------------------------------

    def pix(self, numero_origem: str, numero_destino: str, valor) -> dict:
        """
        Realiza um PIX entre contas (funciona igual à transferência,
        mas registrado com o tipo 'PIX' no extrato).

        Retorna:
            sucesso         (bool)
            mensagem        (str)
            saldo_origem    (float | None)
        """
        erro = self._validar_valor(valor)
        if erro:
            return erro

        valor          = float(valor)
        numero_origem  = numero_origem.strip()
        numero_destino = numero_destino.strip()

        if numero_origem == numero_destino:
            return {"sucesso": False, "mensagem": "Origem e destino não podem ser a mesma conta.", "saldo_origem": None}

        conta_origem  = self.db.buscar_conta(numero_origem)
        conta_destino = self.db.buscar_conta(numero_destino)

        if not conta_origem:
            return {"sucesso": False, "mensagem": f"Conta de origem '{numero_origem}' não encontrada.", "saldo_origem": None}

        if not conta_destino:
            return {"sucesso": False, "mensagem": f"Conta de destino '{numero_destino}' não encontrada.", "saldo_origem": None}

        if not conta_origem.transferir_para(conta_destino, valor):
            return {
                "sucesso":      False,
                "mensagem":     f"Saldo insuficiente para o PIX. Saldo atual: R$ {conta_origem.saldo:,.2f}",
                "saldo_origem": conta_origem.saldo
            }

        self.db.atualizar_saldo(conta_origem)
        self.db.atualizar_saldo(conta_destino)

        transacao = Transacao(
            conta_origem=numero_origem,
            conta_destino=numero_destino,
            tipo="PIX",
            valor=valor
        )
        self.db.registrar_transacao(transacao)

        return {
            "sucesso":      True,
            "mensagem":     f"PIX de R$ {valor:,.2f} enviado para a conta {numero_destino} com sucesso!",
            "saldo_origem": conta_origem.saldo
        }

    # ------------------------------------------------------------------
    # Extrato
    # ------------------------------------------------------------------

    def ver_extrato(self, numero_conta: str) -> dict:
        """
        Retorna o histórico de transações de uma conta.

        Retorna:
            sucesso     (bool)
            mensagem    (str)
            transacoes  (list[Transacao])
        """
        conta = self.db.buscar_conta(numero_conta.strip())

        if not conta:
            return {"sucesso": False, "mensagem": f"Conta '{numero_conta}' não encontrada.", "transacoes": []}

        historico = self.db.buscar_extrato(numero_conta.strip())

        if not historico:
            return {"sucesso": True, "mensagem": "Nenhuma transação encontrada.", "transacoes": []}

        return {
            "sucesso":    True,
            "mensagem":   f"{len(historico)} transação(ões) encontrada(s).",
            "transacoes": historico
        }
