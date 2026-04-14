import os
from database.tables_setup import criar_todas_tabelas
from controllers.auth_controller import AuthController

def main():
    # Garante que as tabelas necessárias existem
    criar_todas_tabelas()

    auth = AuthController()

    print("\n" + "=" * 45)
    print("      SISTEMA BANCÁRIO - TESTE DE AUTH")
    print("=" * 45)

    print("\n[1] REGISTRAR USUÁRIO")
    res1 = auth.registrar("Teste Silva", "123.456.789-00", "senha123")
    print(f"Resultado: {'OK' if res1['sucesso'] else 'ERRO'}: {res1['mensagem']}")

    print("\n[2] TENTAR REGISTRAR CPF DUPLICADO")
    res2 = auth.registrar("Outrante da Silva", "12345678900", "senha123")
    print(f"Resultado: {'OK' if res2['sucesso'] else 'ERRO'}: {res2['mensagem']}")

    print("\n[3] LOGIN FALHO (SENHA ERRADA)")
    res3 = auth.login("123.456.789-00", "senhaerrada")
    print(f"Resultado: {'OK' if res3['sucesso'] else 'ERRO'}: {res3['mensagem']}")

    print("\n[4] LOGIN COM SUCESSO")
    res4 = auth.login("123.456.789-00", "senha123")
    print(f"Resultado: {'OK' if res4['sucesso'] else 'ERRO'}: {res4['mensagem']}")
    print(f"   Sessão Ativa: {auth.obter_usuario_atual()}")
    print(f"   Autorização p/ Telas Internas: {'Concedida' if auth.esta_logado() else 'Negada'}")

    print("\n[5] LOGOUT")
    res5 = auth.logout()
    print(f"Resultado: {'OK' if res5['sucesso'] else 'ERRO'}: {res5['mensagem']}")
    print(f"   Autorização p/ Telas Internas: {'Concedida' if auth.esta_logado() else 'Negada'}")
    print("-" * 45)

if __name__ == "__main__":
    main()
