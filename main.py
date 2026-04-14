"""
main.py
Ponto de entrada do Sistema Bancário.
Serve como interface de testes de back-end via terminal (CLI).

Utiliza os controllers da Pessoa 4:
  - ContaController    (contas/conta_controller.py)
  - TransacaoController (controllers/transacao_controller.py)
"""

import os
from controllers.conta_controller import ContaController
from controllers.transacao_controller import TransacaoController

cc = ContaController()
tc = TransacaoController()


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def linha():
    print("-" * 45)


def exibir_menu():
    print("\n" + "=" * 45)
    print("         SISTEMA BANCARIO  - MENU")
    print("=" * 45)
    print("  [1] Criar Conta")
    print("  [2] Consultar Saldo")
    print("  [3] Depositar")
    print("  [4] Sacar")
    print("  [5] Transferencia")
    print("  [6] PIX")
    print("  [7] Ver Extrato")
    print("  [8] Listar todas as contas")
    print("  [9] Excluir Conta")
    print("  [0] Sair")
    print("-" * 45)


def ler_valor(prompt: str) -> float | None:
    """Lê um valor monetário do usuário com tratamento de erro."""
    try:
        return float(input(prompt).replace(",", "."))
    except ValueError:
        print("[Erro] Valor invalido. Digite um numero.")
        return None


# ------------------------------------------------------------------
# Handlers de cada opcao
# ------------------------------------------------------------------

def criar_conta():
    linha()
    numero = input("Numero da conta: ").strip()
    titular = input("Nome do titular: ").strip()
    saldo_str = input("Saldo inicial (Enter para 0): ").strip() or "0"
    try:
        saldo = float(saldo_str.replace(",", "."))
    except ValueError:
        print("[Erro] Saldo invalido.")
        return
    resultado = cc.criar_conta(numero, titular, saldo)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")


def consultar_saldo():
    linha()
    numero = input("Numero da conta: ").strip()
    resultado = cc.consultar_saldo(numero)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")


def depositar():
    linha()
    numero = input("Numero da conta: ").strip()
    valor = ler_valor("Valor do deposito: R$ ")
    if valor is None:
        return
    resultado = tc.depositar(numero, valor)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")
    if resultado["sucesso"]:
        print(f"   Novo saldo: R$ {resultado['saldo']:,.2f}")


def sacar():
    linha()
    numero = input("Numero da conta: ").strip()
    valor = ler_valor("Valor do saque: R$ ")
    if valor is None:
        return
    resultado = tc.sacar(numero, valor)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")
    if resultado["sucesso"]:
        print(f"   Novo saldo: R$ {resultado['saldo']:,.2f}")


def transferir():
    linha()
    origem = input("Conta de ORIGEM: ").strip()
    destino = input("Conta de DESTINO: ").strip()
    valor = ler_valor("Valor da transferencia: R$ ")
    if valor is None:
        return
    resultado = tc.transferir(origem, destino, valor)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")
    if resultado["sucesso"]:
        print(f"   Saldo restante na origem: R$ {resultado['saldo_origem']:,.2f}")


def pix():
    linha()
    origem = input("Conta de ORIGEM: ").strip()
    destino = input("Conta de DESTINO: ").strip()
    valor = ler_valor("Valor do PIX: R$ ")
    if valor is None:
        return
    resultado = tc.pix(origem, destino, valor)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")
    if resultado["sucesso"]:
        print(f"   Saldo restante na origem: R$ {resultado['saldo_origem']:,.2f}")


def ver_extrato():
    linha()
    numero = input("Numero da conta: ").strip()
    resultado = tc.ver_extrato(numero)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")
    if resultado["sucesso"] and resultado["transacoes"]:
        print()
        for t in resultado["transacoes"]:
            print(f"   {t}")


def listar_contas():
    linha()
    contas = cc.listar_contas()
    if not contas:
        print("\n[Aviso] Nenhuma conta cadastrada.")
        return
    print(f"\n{len(contas)} conta(s) encontrada(s):\n")
    for c in contas:
        print(f"   {c}")


def excluir_conta():
    linha()
    numero = input("Numero da conta a excluir: ").strip()
    confirmacao = input(f"Confirmar exclusao da conta {numero}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("[Cancelado]")
        return
    resultado = cc.excluir_conta(numero)
    print(f"\n{'OK' if resultado['sucesso'] else 'ERRO'}: {resultado['mensagem']}")


# ------------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------------

ACOES = {
    "1": criar_conta,
    "2": consultar_saldo,
    "3": depositar,
    "4": sacar,
    "5": transferir,
    "6": pix,
    "7": ver_extrato,
    "8": listar_contas,
    "9": excluir_conta,
}


def sistema():
    limpar_tela()
    print("Sistema Bancario iniciado.")

    while True:
        exibir_menu()
        opcao = input("Opcao: ").strip()

        if opcao == "0":
            print("\nEncerrando sistema. Ate logo!\n")
            break
        elif opcao in ACOES:
            ACOES[opcao]()
            input("\nPressione Enter para continuar...")
            limpar_tela()
        else:
            print("[Erro] Opcao invalida.")


if __name__ == "__main__":
    sistema()