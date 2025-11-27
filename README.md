# Projeto: Sistema Auxiliar de Investimentos (InvestApp)

*Nome:* Dominic Skiba, João Vicente Kochisnski, Pedro Matta

*Curso:* Bacharelado em Engenharia de Software

*Matéria:* Raciocínio Algorítimico

*Professor:* Maicris Fernandes

# 1. Descrição do Projeto

O InvestApp é uma aplicação web completa construída em Python e Flask. Ela permite que usuários gerenciem suas carteiras de investimento, rastreando tanto Ações da bolsa quanto investimentos de Renda Fixa.

O sistema calcula o desempenho de cada ativo em tempo real, buscado dados de Ações na API do **Yahoo Finance ('yfinance')** e dados de Renda Fixa (CDI) na API oficial do **Banco Central do Brasil (`requests`)**.

# 2. Funcionalidades Principais

- *Autenticação de Usuário:* Sistema de cadastro e login com senhas seguras.
- *Quiz de Perfil:* O usuário responde a 5 perguntas para definir seu perfil de investidor (Conservador, Moderado, Arrojado).
- *Rastreamento de Ações (Bolsa):*
    - Busca de Ações por nome (usando um índice CSV da B3).
    - Geração de gráfico do último ano (com `matplotlib`).
    - Adição à carteira (com base no valor e data da compra).
- *Rastreamento de Renda Fixa:*
    - Adição manual de CDBs, Tesouro, etc.
    - Suporte para cálculo de rendimento Pré-Fixado e Pós-Fixado (% do CDI).
- *Cálculo de Desempenho:* A página "Minha Carteira" calcula o lucro/prejuízo de cada ativo e o total da carteira em tempo real.

# 3. Como Executar o Projeto

*Pré-requisitos:*
- Python 3.x
- Pip (Gerenciador de pacotes do Python)

*Passo 1: Clonar/Baixar o Repositório*
- Baixe os arquivos e extraia-os em uma pasta.

*Passo 2: Instalar as Dependências*
- Abra um terminal na pasta do projeto e execute o comando:

**pip install -r requirements.txt**
**Recomendamos utilizar a Extenção 'SQLite' do autor alexcvzz**

*Passo 3: Iniciar o Proejeto*
- Inicie o Arquivo **main.py**
- Certifique-se de que a pasta **__pycache__** e o arquivo **invest.db** sejam deletados
