# 🏦 Python Bank App (Fintech Acadêmica)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)

Um aplicativo bancário simulado, desenvolvido em Python, focado em operações financeiras essenciais e no conceito de integração de contas (Open Banking). Projeto desenvolvido como requisito avaliativo para o curso de Análise e Desenvolvimento de Sistemas.

## 👥 Equipe (Grupo 4) e Divisão de Tarefas
* **[Nome do Membro 1] - Front-end A:** Telas Iniciais (Autenticação e dados cadastrais). Trabalha na camada `views/login_cadastro.py`.
* **[Nome do Membro 2] - Front-end B:** Telas Internas (Dashboard, transações, extrato). Trabalha no restante da camada `views`.
* **[Nome do Membro 3] - Back-end A:** Autenticação e Usuários (Lógica de login, proteção de telas, modelos de usuário). Trabalha em `controllers/auth_controller.py` e `models`.
* **[Nome do Membro 4] - Back-end B & Banco de Dados:** Regras de negócio matemáticas (saldo, saques, extato) e controle da persistência (Tabelas e SQLite). Trabalha em `controllers`, `models` e em modo chefe de toda a pasta `database`.
* **[Nome do Membro 5] - Documentação:** Exclusivamente responsável por elaborar toda a documentação das vantagens/desvantagens para a apresentação teórica do sistema.

## 📁 Arquitetura do Projeto (MVC Simplificado)

Nossa estrutura de arquivos foi pensada para que as 5 pessoas consigam trabalhar de forma independente sem gerar conflitos e dividir as áreas de atuação:

```text
BancoCRUD/
├── main.py                   # Ponto de entrada (Inicia o app e roteia)
|── app_api.py                # linka com o front 
├── README.md                 # Documentação (Pessoa 5)
├── requirements.txt          # Dependências do projeto
│
├── database/                 # 🗄️ RESPONSABILIDADE: Pessoa 4
│   ├── banco_sqlite.py       # Funções base de conexão com o banco
│   └── tables_setup.py       # Script para criar tabelas iniciais
│
├── models/                   # 🏗️ RESPONSABILIDADE: Pessoas 3 e 4
│   ├── model_usuario.py      # Classe Usuário (Pessoa 3)
│   ├── model_conta.py        # Classe Conta (Pessoa 4)
│   └── model_transacao.py    # Classe Transação (Pessoa 4)
│
├── controllers/              # ⚙️ RESPONSABILIDADE: Pessoas 3 e 4 (Regras Lógicas)
│   ├── auth_controller.py    # Login/Cadastro/Sessão (Pessoa 3)
│   ├── conta_controller.py   # Consultas e criação de conta (Pessoa 4)
│   └── transacao_controller.py # Validar depósitos, saques, PIX (Pessoa 4)
│
├── frontend/                    # 🎨 RESPONSABILIDADE: Pessoas 1 e 2 (Telas Visuais)
│   ├── app.js 
|   |── index.html                 
│   └── style.css          
│
└── utils/                    # 🛠️ UTILITÁRIOS GERAIS
    ├── validacoes.py         # Tratamento de erros, validações de CPF, etc.
    └── formatadores.py       # Formatação de datas, moedas, etc.
```

## 🎯 Escopo do Projeto

O objetivo deste aplicativo não é ser um sistema perfeito e comercializável, mas sim demonstrar o domínio sobre fluxos de dados, operações lógicas condicionais e persistência de dados em Python. 

### Tema da Apresentação: Integração de Sistemas
* **Vantagens:** Reutilização de código, facilidade de escalabilidade e centralização de informações (ex: demonstrativo de saldos de vários bancos na mesma tela).
* **Desvantagens:** Maior complexidade arquitetural, aumento de custos operacionais e possível latência nas requisições.

## ⚙️ Funcionalidades

- [ ] **Sistema de Autenticação:** Login e Cadastro de novos usuários.
- [ ] **Simulação Open Banking:** Vinculação da conta com instituições parceiras (Itaú, Nubank, C6, etc).
- [ ] **Verificação de Saldo:** Consulta em tempo real do saldo consolidado.
- [ ] **Operações de Saque:** Retirada de valores com validação de saldo em conta.
- [ ] **Depósitos (PIX e DOC):** Entrada de valores simulando chaves instantâneas e transferências bancárias.
- [ ] **Transferências:** Envio de valores para terceiros.
- [ ] **Extrato Bancário:** Histórico detalhado de entradas e saídas.

## 💻 Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Interface Gráfica:** [Defina aqui se usarão Tkinter, CustomTkinter, ou apenas terminal/CLI]
* **Banco de Dados:** SQLite (para armazenamento leve e local das contas e transações)

## 🚀 Como executar o projeto

Clone este repositório:
   ```bash
   git clone https://github.com/gab-malves/BancoCRUD
   ```
# 1. Instalar dependências
pip install flask flask-cors

# 2. Subir a API (dentro da pasta BancoCRUD/)
python app_api.py

# 3. Abrir o front no VS Code com Live Server
# Clique direito em index.html → Open with Live Server