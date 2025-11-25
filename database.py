import sqlite3
import os

DB_PASTA = "db" 
DB_NOME = os.path.join(DB_PASTA, "invest.db")

def iniciar_banco():
    os.makedirs(DB_PASTA, exist_ok=True)
    
    db = sqlite3.connect(DB_NOME)
    cursor = db.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, 
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ativos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        ticker TEXT, 
        tipo TEXT NOT NULL, 
        perfil_alvo TEXT NOT NULL, 
        rendimento_ultimo_ano TEXT,
        valor_minimo REAL,
        prazo_saque TEXT,
        banco_corretora TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posicoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        id_ativo INTEGER NOT NULL,
        valor_investido REAL NOT NULL, 
        data_compra TEXT NOT NULL,
        tipo_rendimento TEXT, 
        taxa REAL, 
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
        FOREIGN KEY (id_ativo) REFERENCES ativos (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        valor_alvo REAL NOT NULL,
        data_limite TEXT,
        concluida INTEGER DEFAULT 0,
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
    )
    """)
    
    db.commit()
    db.close()
    print("Banco de dados iniciado.")