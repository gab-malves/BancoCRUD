import sqlite3
from models.model_conta import Conta

class BancoDados:
    def __init__(self):
        self.db_name = "sistema_bancario.db"
        self.criar_tabela()

    def conectar(self):
        #Conexão com o arquivo local
        return sqlite3.connect(self.db_name)
    
    def criar_tabela(self):
        #conn vem de connect
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contas (
                    numero TEXT PRIMARY KEY,
                    titular TEXT,
                    saldo REAL
                )
            """)
            conn.commit()

    def salvar_conta(self, conta):
        with self.conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO contas (numero, titular, saldo) VALUES (?, ?, ?)", (conta.numero, conta.titular, conta.saldo))
                conn.commit()
            except sqlite3.IntegrityError:
                print("\n[Erro] Já existe uma conta com esse número.")

    def buscar_conta(self, numero):
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contas WHERE numero = ?", (numero,))
            dados = cursor.fetchone()
            if dados:
                return Conta(dados[0], dados[1], dados[2])
            return None
        
    def atualizar_saldo(self, conta):
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contas SET saldo = ? WHERE numero = ?", (conta.saldo, conta.numero))
            conn.commit()