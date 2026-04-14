"""
auth_controller.py
Responsabilidade: Pessoa 3 - Back-end A

Controlador responsável por gerenciar registros, logins e sessão de usuário.
As consultas ao banco de dados relacionadas a usuários são mantidas internamente 
neste controlador conforme requisitado pelas diretrizes dadas.
"""
import sqlite3
import hashlib
from typing import Optional
from database.tables_setup import DB_NAME
from models.model_usuario import Usuario
from utils.validacoes import limpar_cpf

class AuthController:
    def __init__(self):
        # Gerenciamento de sessão: carrega o model gerado toda evz que um login é feito com sucesso
        self.usuario_logado: Optional[Usuario] = None

    def _conectar(self) -> sqlite3.Connection:
        """Facilita a conexão pontual com o DB gerado na nossa área central de arquivos (banco de dados SQLite)."""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    def _gerar_hash_senha(self, senha: str) -> str:
        """Gera um hash SHA-256 para a senha."""
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()

    def registrar(self, nome: str, cpf: str, senha: str) -> dict:
        """
        Registra um novo usuário no banco de dados da Pessoa 4 diretamente utilizando queries cruas.
        Retorna dicionário com sucesso e mensagem correspondente.
        """
        cpf_limpo = limpar_cpf(cpf)
        
        # Filtros de erros que vão diretamente para a interface para alertar o usuário:
        if not nome or not senha or not cpf_limpo:
            return {"sucesso": False, "mensagem": "Todos os campos são obrigatórios."}
        
        # Só é gerado um hash quando tudo estiver de acordo com as regras:
        senha_hash = self._gerar_hash_senha(senha)

        try:
            with self._conectar() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (nome, cpf, senha_hash) VALUES (?, ?, ?)",
                    (nome, cpf_limpo, senha_hash)
                )
                conn.commit()
            return {"sucesso": True, "mensagem": "Usuário registrado com sucesso."}
        except sqlite3.IntegrityError:
            # Pega o erro que criamos com o "UNIQUE" no SQL schema
            return {"sucesso": False, "mensagem": "Este CPF já encontra-se cadastrado no sistema."}
        except Exception as e:
            return {"sucesso": False, "mensagem": f"Erro interno ao criar usuário (DB): {e}"}

    def login(self, cpf: str, senha: str) -> dict:
        """
        Realiza o login. Busca o usuario usando os Hashs previamente gerados pelo método _gerar_hash_senha
        Quando batem, a sessão do usuário começa.
        """
        cpf_limpo = limpar_cpf(cpf)
        senha_hash = self._gerar_hash_senha(senha)

        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nome, cpf FROM usuarios WHERE cpf = ? AND senha_hash = ?",
                (cpf_limpo, senha_hash)
            )
            dados = cursor.fetchone()

        if dados:
            # Login bem-sucedido
            self.usuario_logado = Usuario(id=dados["id"], nome=dados["nome"], cpf=dados["cpf"])
            return {"sucesso": True, "mensagem": f"Bem-vindo(a), {self.usuario_logado.nome}!"}
        
        return {"sucesso": False, "mensagem": "CPF ou senha incorretos."}

    def logout(self) -> dict:
        """Encerra a sessão do usuário atual para a renderização das telas internas sem as informações passadas."""
        if self.usuario_logado:
            self.usuario_logado = None
            return {"sucesso": True, "mensagem": "Logout realizado com sucesso."}
        return {"sucesso": False, "mensagem": "Nenhum usuário logado."}

    def esta_logado(self) -> bool:
        """Retorna True se há alguém logado, False caso contrário. Essencial para verificar autenticação de acesso"""
        return self.usuario_logado is not None

    def obter_usuario_atual(self) -> Optional[Usuario]:
        """Retorna as informações do model para uso de query"""
        return self.usuario_logado
