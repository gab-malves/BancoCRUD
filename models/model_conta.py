"""
model_conta.py
Responsabilidade: Pessoa 4 - Back-end B & Banco de Dados

Modelo de dados que representa uma Conta Bancária.
Contém apenas os atributos e as regras de negócio matemáticas
internas à conta (sem acesso direto ao banco de dados).
"""


class Conta:
    """
    Representa uma conta bancária do sistema.

    Atributos:
        numero   (str):   Identificador único da conta (ex: "0001-2")
        titular  (str):   Nome completo do titular
        saldo    (float): Saldo atual disponível na conta
    """

    def __init__(self, numero: str, titular: str, saldo: float = 0.0):
        self.numero  = numero
        self.titular = titular
        self.saldo   = saldo

    # ------------------------------------------------------------------
    # Regras de negócio matemáticas
    # ------------------------------------------------------------------

    def depositar(self, valor: float) -> bool:
        """
        Adiciona 'valor' ao saldo da conta.
        Retorna True em caso de sucesso, False se valor for inválido.
        """
        if valor <= 0:
            return False
        self.saldo += valor
        return True

    def sacar(self, valor: float) -> bool:
        """
        Debita 'valor' do saldo da conta.
        Retorna True em caso de sucesso.
        Retorna False se valor for inválido ou saldo insuficiente.
        """
        if valor <= 0:
            return False
        if valor > self.saldo:
            return False
        self.saldo -= valor
        return True

    def transferir_para(self, outra_conta: "Conta", valor: float) -> bool:
        """
        Realiza uma transferência desta conta para outra_conta.
        Debita desta conta e credita na outra atomicamente (em memória).
        A persistência deve ser feita pelo controller.
        Retorna True em caso de sucesso.
        """
        if self.sacar(valor):
            outra_conta.depositar(valor)
            return True
        return False

    # ------------------------------------------------------------------
    # Representação
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "numero": self.numero,
            "titular": self.titular,
            "saldo": self.saldo
        }

    def __str__(self) -> str:
        return (
            f"Conta: {self.numero} | "
            f"Titular: {self.titular} | "
            f"Saldo: R$ {self.saldo:,.2f}"
        )

    def __repr__(self) -> str:
        return f"Conta(numero={self.numero!r}, titular={self.titular!r}, saldo={self.saldo})"