"""
banco_sqlite.py
Responsabilidade: Pessoa 4 - Back-end B & Banco de Dados

Módulo central de acesso ao banco de dados SQLite.
Fornece a classe BancoDados com todos os métodos de consulta e persistência
para contas e transações.
"""

import sqlite3
from database.tables_setup import criar_todas_tabelas, DB_NAME
from models.model_conta import Conta
from models.model_transacao import Transacao


class BancoDados:
    """
    Classe responsável por toda a comunicação com o banco de dados SQLite.
    Gerencia operações de Conta e Transação (CRUD completo).
    """

    def __init__(self):
        # Garante que as tabelas existam ao iniciar o sistema
        criar_todas_tabelas()

    # ------------------------------------------------------------------
    # Utilitário: conexão
    # ------------------------------------------------------------------

    def conectar(self) -> sqlite3.Connection:
        """Retorna uma conexão ativa com o banco de dados."""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
        return conn

    # ------------------------------------------------------------------
    # Operações de CONTA
    # ------------------------------------------------------------------

    def salvar_conta(self, conta: Conta) -> bool:
        """
        Persiste uma nova conta no banco de dados.
        Retorna True em caso de sucesso, False se o número já existir.
        """
        try:
            with self.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO contas (numero, titular, saldo) VALUES (?, ?, ?)",
                    (conta.numero, conta.titular, conta.saldo)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def buscar_conta(self, numero: str) -> Conta | None:
        """
        Busca uma conta pelo número.
        Retorna um objeto Conta ou None se não encontrada.
        """
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contas WHERE numero = ?", (numero,))
            dados = cursor.fetchone()

        if dados:
            return Conta(dados["numero"], dados["titular"], dados["saldo"])
        return None

    def listar_contas(self) -> list[Conta]:
        """
        Retorna uma lista com todas as contas cadastradas.
        """
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contas ORDER BY titular")
            linhas = cursor.fetchall()

        return [Conta(l["numero"], l["titular"], l["saldo"]) for l in linhas]

    def atualizar_saldo(self, conta: Conta) -> None:
        """
        Atualiza o saldo de uma conta existente no banco.
        """
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contas SET saldo = ? WHERE numero = ?",
                (conta.saldo, conta.numero)
            )
            conn.commit()

    def excluir_conta(self, numero: str) -> bool:
        """
        Remove uma conta do banco de dados.
        Retorna True se alguma linha foi afetada.
        """
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contas WHERE numero = ?", (numero,))
            conn.commit()
            return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Operações de TRANSAÇÃO
    # ------------------------------------------------------------------

    def registrar_transacao(self, transacao: Transacao) -> None:
        """
        Persiste um registro de transação no histórico.
        """
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transacoes (conta_origem, conta_destino, tipo, valor, descricao)
                VALUES (?, ?, ?, ?, ?)
            """, (
                transacao.conta_origem,
                transacao.conta_destino,
                transacao.tipo,
                transacao.valor,
                transacao.descricao
            ))
            conn.commit()

    def buscar_extrato(self, numero_conta: str) -> list[Transacao]:
        """
        Retorna o extrato (histórico) de uma conta, ordenado do mais recente ao mais antigo.
        """
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transacoes
                WHERE conta_origem = ? OR conta_destino = ?
                ORDER BY realizada_em DESC
            """, (numero_conta, numero_conta))
            linhas = cursor.fetchall()

        return [
            Transacao(
                conta_origem=l["conta_origem"],
                tipo=l["tipo"],
                valor=l["valor"],
                conta_destino=l["conta_destino"],
                descricao=l["descricao"],
                realizada_em=l["realizada_em"]
            )
            for l in linhas
        ]