from models import Conta
from database import BancoDados
import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_menu():
    print("\n=== BANCO ===\n"
          "1. Criar Conta\n"
          "2. Consultar Saldo\n"
          "3. Depositar\n"
          "4. Sacar\n"
          "0. Sair")


def sistema():
    db = BancoDados() #inicia o banco de dados

    while True:
        exibir_menu()
        opcao = input("Opção: ")

        if opcao == "1":
            num = input("Número da conta: ")
            nome = input("Titular: ")
            nova_conta = Conta(num, nome)
            db.salvar_conta(nova_conta)
            print("Conta registrada com sucesso!")
            limpar_tela()

        elif opcao == "2":
            num = input("Número da conta: ")
            conta = db.buscar_conta(num)
            if conta:
                print(f"\n{conta}")
            else:
                print("\nConta não encontrada.")
            limpar_tela()
            
        elif opcao == "3":
            num = input("Número da conta: ")
            conta = db.buscar_conta(num)
            if conta:
                valor = float(input("Valor do depósito: "))
                conta.depositar(valor)
                db.atualizar_saldo(conta)
                print("Depósito realizado!")
            else:
                print("Conta inexistente.")
            limpar_tela()

        elif opcao == "4":
            num = input("Número: ")
            conta = db.buscar_conta(num)
            if conta:
                valor = float(input("Valor do saque: "))
                if conta.sacar(valor):
                    db.atualizar_saldo(conta)
                    print("Saque realizado!")
                else:
                    print("Saldo insuficiente.")
            else:
                print("Conta inexistente.")
            limpar_tela()
                
        elif opcao == "0":
            print("Encerrando...")
            break

if __name__ == "__main__":
    sistema()