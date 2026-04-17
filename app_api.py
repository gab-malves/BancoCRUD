"""
app_api.py
==========
API REST (Flask) que expõe todos os controllers do BancoCRUD para o front-end web.

Instalar dependências:
    pip install flask flask-cors

Rodar:
    python app_api.py

A API sobe em: http://localhost:5000
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import hashlib
import sqlite3
import os

# ── Importa os controllers existentes do projeto ──────────────────────────────
from controllers.conta_controller import ContaController
from controllers.transacao_controller import TransacaoController

# ── Importa setup do banco para garantir que as tabelas existam ───────────────
from database.tables_setup import criar_todas_tabelas

app = Flask(__name__)
app.secret_key = "bancocrud_secret_2024"   # Troque em produção
CORS(app, supports_credentials=True)

# Inicializa controllers
cc = ContaController()
tc = TransacaoController()

# ── Garante tabelas ao subir ───────────────────────────────────────────────────
criar_todas_tabelas()

# ─────────────────────────────────────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────────────────────────────────────

def _hash(senha: str) -> str:
    """Hash SHA-256 simples para senhas de usuários."""
    return hashlib.sha256(senha.encode()).hexdigest()


def _get_db():
    """Retorna conexão com o banco SQLite do projeto."""
    db_path = os.path.join(os.path.dirname(__file__), "sistema_bancario.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _garantir_tabela_usuarios():
    """Cria a tabela de usuários da fintech se ainda não existir."""
    conn = _get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_fintech (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            senha_hash  TEXT NOT NULL,
            nome        TEXT NOT NULL,
            data_nasc   TEXT,
            cpf         TEXT UNIQUE,
            cep         TEXT,
            logradouro  TEXT,
            bairro      TEXT,
            cidade      TEXT,
            uf          TEXT,
            banco       TEXT,
            conta_num   TEXT,
            criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


_garantir_tabela_usuarios()


# ─────────────────────────────────────────────────────────────────────────────
# AUTENTICAÇÃO  (/auth/*)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/auth/registrar", methods=["POST"])
def registrar():
    """
    Cadastra novo usuário + cria conta na fintech.
    Body JSON esperado:
    {
        "username":   "joao123",
        "senha":      "minhasenha",
        "nome":       "João Silva",
        "data_nasc":  "1995-04-10",
        "cpf":        "123.456.789-00",
        "cep":        "01310-100",
        "logradouro": "Av. Paulista",
        "bairro":     "Bela Vista",
        "cidade":     "São Paulo",
        "uf":         "SP",
        "banco":      "Nubank",
        "saldo_ini":  1000.00        (opcional)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"sucesso": False, "mensagem": "Dados inválidos."}), 400

    username  = data.get("username", "").strip()
    senha     = data.get("senha", "").strip()
    nome      = data.get("nome", "").strip()
    data_nasc = data.get("data_nasc", "")
    cpf       = data.get("cpf", "").strip()
    cep       = data.get("cep", "").strip()
    logradouro= data.get("logradouro", "")
    bairro    = data.get("bairro", "")
    cidade    = data.get("cidade", "")
    uf        = data.get("uf", "")
    banco     = data.get("banco", "")
    saldo_ini = float(data.get("saldo_ini") or 0)

    if not username or not senha or not nome:
        return jsonify({"sucesso": False, "mensagem": "Usuário, senha e nome são obrigatórios."}), 400

    conn = _get_db()
    try:
        conn.execute("""
            INSERT INTO usuarios_fintech
                (username, senha_hash, nome, data_nasc, cpf, cep,
                 logradouro, bairro, cidade, uf, banco)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (username, _hash(senha), nome, data_nasc, cpf, cep,
              logradouro, bairro, cidade, uf, banco))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        if "username" in str(e):
            return jsonify({"sucesso": False, "mensagem": "Nome de usuário já existe."}), 409
        if "cpf" in str(e):
            return jsonify({"sucesso": False, "mensagem": "CPF já cadastrado."}), 409
        return jsonify({"sucesso": False, "mensagem": "Erro ao cadastrar."}), 409

    # Cria conta bancária automaticamente com o número = username
    resultado = cc.criar_conta(username, nome, saldo_ini)
    conn.close()

    if not resultado["sucesso"]:
        # Usuário criado mas conta pode já existir — não é erro fatal
        pass

    return jsonify({"sucesso": True, "mensagem": "Cadastro realizado com sucesso!"}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    """
    Autentica usuário.
    Body JSON: { "username": "...", "senha": "..." }
    """
    data = request.get_json()
    username = data.get("username", "").strip()
    senha    = data.get("senha", "").strip()

    conn = _get_db()
    row = conn.execute(
        "SELECT * FROM usuarios_fintech WHERE username = ? AND senha_hash = ?",
        (username, _hash(senha))
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"sucesso": False, "mensagem": "Usuário ou senha inválidos."}), 401

    session["username"] = username
    session["nome"]     = row["nome"]

    return jsonify({
        "sucesso":  True,
        "mensagem": f"Bem-vindo, {row['nome']}!",
        "usuario":  {
            "username":   username,
            "nome":       row["nome"],
            "banco":      row["banco"],
            "conta_num":  username,
        }
    })


@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"sucesso": True, "mensagem": "Sessão encerrada."})


# ─────────────────────────────────────────────────────────────────────────────
# CONTAS  (/contas/*)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/contas", methods=["POST"])
def criar_conta():
    """
    Cria uma conta bancária.
    Body JSON: { "numero": "1001", "titular": "Maria", "saldo": 500.0 }
    """
    data    = request.get_json()
    numero  = str(data.get("numero", "")).strip()
    titular = str(data.get("titular", "")).strip()
    saldo   = float(data.get("saldo") or 0)

    if not numero or not titular:
        return jsonify({"sucesso": False, "mensagem": "Número e titular são obrigatórios."}), 400

    resultado = cc.criar_conta(numero, titular, saldo)
    status    = 201 if resultado["sucesso"] else 409
    return jsonify(resultado), status


@app.route("/contas", methods=["GET"])
def listar_contas():
    """Retorna lista de todas as contas."""
    contas = cc.listar_contas()
    resultado = []
    for c in contas:
        if hasattr(c, "to_dict"):
            resultado.append(c.to_dict())
        elif isinstance(c, dict):
            resultado.append(c)
        else:
            resultado.append({"info": str(c)})
    return jsonify({"sucesso": True, "contas": resultado})


@app.route("/contas/<numero>", methods=["GET"])
def consultar_saldo(numero):
    """Consulta saldo de uma conta específica."""
    resultado = cc.consultar_saldo(numero)
    status    = 200 if resultado["sucesso"] else 404
    return jsonify(resultado), status


@app.route("/contas/<numero>", methods=["DELETE"])
def excluir_conta(numero):
    """Exclui uma conta."""
    resultado = cc.excluir_conta(numero)
    status    = 200 if resultado["sucesso"] else 404
    return jsonify(resultado), status


# ─────────────────────────────────────────────────────────────────────────────
# TRANSAÇÕES  (/transacoes/*)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/transacoes/deposito", methods=["POST"])
def depositar():
    """
    Realiza depósito.
    Body JSON: { "numero": "1001", "valor": 200.0 }
    """
    data   = request.get_json()
    numero = str(data.get("numero", "")).strip()
    valor  = float(data.get("valor") or 0)

    if not numero or valor <= 0:
        return jsonify({"sucesso": False, "mensagem": "Número e valor positivo são obrigatórios."}), 400

    resultado = tc.depositar(numero, valor)
    status    = 200 if resultado["sucesso"] else 400
    return jsonify(resultado), status


@app.route("/transacoes/saque", methods=["POST"])
def sacar():
    """
    Realiza saque.
    Body JSON: { "numero": "1001", "valor": 100.0 }
    """
    data   = request.get_json()
    numero = str(data.get("numero", "")).strip()
    valor  = float(data.get("valor") or 0)

    if not numero or valor <= 0:
        return jsonify({"sucesso": False, "mensagem": "Número e valor positivo são obrigatórios."}), 400

    resultado = tc.sacar(numero, valor)
    status    = 200 if resultado["sucesso"] else 400
    return jsonify(resultado), status


@app.route("/transacoes/transferencia", methods=["POST"])
def transferir():
    """
    Realiza transferência entre contas.
    Body JSON: { "origem": "1001", "destino": "1002", "valor": 150.0 }
    """
    data    = request.get_json()
    origem  = str(data.get("origem", "")).strip()
    destino = str(data.get("destino", "")).strip()
    valor   = float(data.get("valor") or 0)

    if not origem or not destino or valor <= 0:
        return jsonify({"sucesso": False, "mensagem": "Origem, destino e valor são obrigatórios."}), 400

    resultado = tc.transferir(origem, destino, valor)
    status    = 200 if resultado["sucesso"] else 400
    return jsonify(resultado), status


@app.route("/transacoes/pix", methods=["POST"])
def pix():
    """
    Realiza PIX.
    Body JSON: { "origem": "1001", "destino": "1002", "valor": 50.0 }
    """
    data    = request.get_json()
    origem  = str(data.get("origem", "")).strip()
    destino = str(data.get("destino", "")).strip()
    valor   = float(data.get("valor") or 0)

    if not origem or not destino or valor <= 0:
        return jsonify({"sucesso": False, "mensagem": "Origem, destino e valor são obrigatórios."}), 400

    resultado = tc.pix(origem, destino, valor)
    status    = 200 if resultado["sucesso"] else 400
    return jsonify(resultado), status


@app.route("/transacoes/extrato/<numero>", methods=["GET"])
def extrato(numero):
    """Retorna extrato de uma conta."""
    resultado = tc.ver_extrato(numero)
    if resultado["sucesso"] and "transacoes" in resultado:
        lista_json = []
        for t in resultado["transacoes"]:
            if hasattr(t, "to_dict"):
                tdict = t.to_dict()
                # O front espera valores negativos se for um débito para esta conta
                if t.eh_debito(numero):
                    tdict["valor"] = -tdict["valor"]
                lista_json.append(tdict)
            else:
                lista_json.append(str(t))
        resultado["transacoes"] = lista_json

    status = 200 if resultado["sucesso"] else 404
    return jsonify(resultado), status


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD  (/dashboard)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Retorna dados agregados para o dashboard:
    - saldo_total de todas as contas
    - numero_contas
    - ultimas transações (para o gráfico)
    """
    contas = cc.listar_contas()

    saldo_total  = 0.0
    num_contas   = 0
    resumo_contas = []

    for c in contas:
        num_contas += 1
        cdict = c.to_dict() if hasattr(c, "to_dict") else c if isinstance(c, dict) else {}
        if cdict:
            saldo = float(cdict.get("saldo", 0))
            saldo_total += saldo
            resumo_contas.append({
                "numero":  cdict.get("numero", ""),
                "titular": cdict.get("titular", ""),
                "saldo":   saldo,
            })

    return jsonify({
        "sucesso":       True,
        "saldo_total":   saldo_total,
        "num_contas":    num_contas,
        "contas":        resumo_contas,
    })


# ─────────────────────────────────────────────────────────────────────────────
# CEP  (/cep/<cep>)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/cep/<cep>", methods=["GET"])
def buscar_cep(cep):
    """
    Proxy para ViaCEP — evita problemas de CORS no front-end.
    Retorna logradouro, bairro, cidade, uf para o formulário de cadastro.
    """
    import urllib.request
    import json as _json

    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    if len(cep_limpo) != 8:
        return jsonify({"sucesso": False, "mensagem": "CEP inválido."}), 400

    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            dados = _json.loads(resp.read().decode())

        if dados.get("erro"):
            return jsonify({"sucesso": False, "mensagem": "CEP não encontrado."}), 404

        return jsonify({
            "sucesso":    True,
            "logradouro": dados.get("logradouro", ""),
            "bairro":     dados.get("bairro", ""),
            "cidade":     dados.get("localidade", ""),
            "uf":         dados.get("uf", ""),
            "cep":        dados.get("cep", ""),
        })
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": f"Erro ao buscar CEP: {e}"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  BancoCRUD API rodando em http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)