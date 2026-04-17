"""
model_transacao.py
Responsabilidade: Pessoa 4 - Back-end B & Banco de Dados

Modelo de dados que representa uma Transação Financeira.
Cada depósito, saque, PIX ou transferência gera um objeto Transacao
que é persistido no histórico do banco de dados.
"""

from datetime import datetime


# Tipos de transação aceitos pelo sistema
TIPOS_VALIDOS = {"DEPOSITO", "SAQUE", "TRANSFERENCIA", "PIX"}


class Transacao:
    """
    Representa um registro de movimentação financeira.

    Atributos:
        conta_origem  (str):   Número da conta que originou a transação
        tipo          (str):   Tipo: 'DEPOSITO', 'SAQUE', 'TRANSFERENCIA' ou 'PIX'
        valor         (float): Valor movimentado (sempre positivo)
        conta_destino (str):   Número da conta destino (opcional, usado em transferências/PIX)
        descricao     (str):   Texto descritivo opcional
        realizada_em  (str):   Data e hora da transação (preenchida automaticamente se vazia)
    """

    def __init__(
        self,
        conta_origem: str,
        tipo: str,
        valor: float,
        conta_destino: str | None = None,
        descricao: str | None = None,
        realizada_em: str | None = None
    ):
        tipo = tipo.upper()
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo de transação inválido: '{tipo}'. Use: {TIPOS_VALIDOS}")
        if valor <= 0:
            raise ValueError(f"O valor da transação deve ser positivo. Recebido: {valor}")

        self.conta_origem  = conta_origem
        self.conta_destino = conta_destino
        self.tipo          = tipo
        self.valor         = valor
        self.descricao     = descricao or self._descricao_padrao()
        self.realizada_em  = realizada_em or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Utilitários internos
    # ------------------------------------------------------------------

    def _descricao_padrao(self) -> str:
        """Gera uma descrição automática com base no tipo da transação."""
        mapa = {
            "DEPOSITO":     f"Depósito de R$ {self.valor:,.2f}",
            "SAQUE":        f"Saque de R$ {self.valor:,.2f}",
            "TRANSFERENCIA": f"Transferência de R$ {self.valor:,.2f} para {self.conta_destino or '?'}",
            "PIX":          f"PIX de R$ {self.valor:,.2f} para {self.conta_destino or '?'}",
        }
        return mapa.get(self.tipo, "Transação")

    def eh_credito(self, numero_conta: str) -> bool:
        """
        Retorna True se esta transação representa uma ENTRADA de dinheiro
        para a conta informada (ex: receber um PIX / depósito).
        """
        return self.conta_destino == numero_conta and self.tipo in {"TRANSFERENCIA", "PIX"}

    def eh_debito(self, numero_conta: str) -> bool:
        """
        Retorna True se esta transação representa uma SAÍDA de dinheiro
        da conta informada.
        """
        return self.conta_origem == numero_conta

    # ------------------------------------------------------------------
    # Representação
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "conta_origem": self.conta_origem,
            "tipo": self.tipo,
            "valor": self.valor,
            "conta_destino": self.conta_destino,
            "descricao": self.descricao,
            "realizada_em": self.realizada_em
        }

    def __str__(self) -> str:
        return (
            f"[{self.realizada_em}] {self.tipo}{' -> ' + self.conta_destino if self.conta_destino else ''} | "
            f"R$ {self.valor:,.2f} | {self.descricao}"
        )

    def __repr__(self) -> str:
        return (
            f"Transacao(tipo={self.tipo!r}, valor={self.valor}, "
            f"origem={self.conta_origem!r}, destino={self.conta_destino!r})"
        )
