"""
tables_setup.py
Responsabilidade: Pessoa 4 - Back-end B & Banco de Dados

Script responsável por criar todas as tabelas do banco de dados SQLite.
Execute este arquivo diretamente para recriar/resetar o esquema do banco.
"""

import sqlite3

DB_NAME = "sistema_bancario.db"


def criar_todas_tabelas():
    """
    Cria todas as tabelas necessárias para o sistema bancário.
    Utiliza CREATE TABLE IF NOT EXISTS para evitar erros ao executar mais de uma vez.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Tabela de Usuários (gerenciada pela Pessoa 3, criada aqui centralmente)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT    NOT NULL,
                cpf         TEXT    NOT NULL UNIQUE,
                senha_hash  TEXT    NOT NULL,
                criado_em   TEXT    DEFAULT (datetime('now', 'localtime'))
            )
        """)

        # Tabela de Contas Bancárias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                numero      TEXT    PRIMARY KEY,
                titular     TEXT    NOT NULL,
                saldo       REAL    NOT NULL DEFAULT 0.0,
                usuario_id  INTEGER,
                criada_em   TEXT    DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

        # Tabela de Transações (histórico completo)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                conta_origem    TEXT    NOT NULL,
                conta_destino   TEXT,
                tipo            TEXT    NOT NULL,   -- 'DEPOSITO', 'SAQUE', 'TRANSFERENCIA', 'PIX'
                valor           REAL    NOT NULL,
                descricao       TEXT,
                realizada_em    TEXT    DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (conta_origem)  REFERENCES contas(numero),
                FOREIGN KEY (conta_destino) REFERENCES contas(numero)
            )
        """)

        conn.commit()
        print("[DB] Todas as tabelas foram criadas/verificadas com sucesso.")


if __name__ == "__main__":
    criar_todas_tabelas()
