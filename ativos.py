import sqlite3
import database
import yfinance as yf

def get_todas_acoes():
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    sql_select = "SELECT * FROM ativos WHERE tipo = 'Ação' ORDER BY nome"
    
    cursor.execute(sql_select)
    lista_de_acoes = cursor.fetchall()
    db.close()
    
    return lista_de_acoes

def get_ativo_by_id(id_ativo):
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    sql_select = "SELECT * FROM ativos WHERE id = ?"
    
    cursor.execute(sql_select, (id_ativo,))
    ativo = cursor.fetchone()
    db.close()
    
    return ativo
    
def get_or_create_ativo_manual(nome, tipo, perfil_alvo):
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    sql_find = "SELECT * FROM ativos WHERE nome = ? AND tipo = ?"
    cursor.execute(sql_find, (nome, tipo))
    ativo_existente = cursor.fetchone()
    
    if ativo_existente:
        db.close()
        return ativo_existente['id']

    try:
        rendimento_ano = "N/A (calculado na carteira)"
        valor_min_float = 0.0
        prazo_saque = "N/A"
        corretora = "Usuário"
    
        sql_insert = """
        INSERT INTO ativos (nome, ticker, tipo, perfil_alvo, rendimento_ultimo_ano, valor_minimo, prazo_saque, banco_corretora)
        VALUES (?, NULL, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(sql_insert, (nome, tipo, perfil_alvo, rendimento_ano, valor_min_float, prazo_saque, corretora))
        
        id_novo = cursor.lastrowid
        
        db.commit()
        db.close()
        
        return id_novo
        
    except Exception as e:
        db.close()
        print(f"Erro ao criar ativo manual: {e}")
        return None
    
def get_or_create_ativo_by_ticker(ticker_simbolo):
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM ativos WHERE ticker = ?", (ticker_simbolo,))
    ativo_no_banco = cursor.fetchone()
    
    if ativo_no_banco:
        db.close()
        return ativo_no_banco
    
    ticker_completo = ticker_simbolo.upper() + ".SA"
    try:
        ticker_yf = yf.Ticker(ticker_completo)
        info = ticker_yf.info
        if not info or info.get('regularMarketPrice') is None:
            db.close()
            return None

        nome = info.get('shortName', info.get('longName', ticker_simbolo))
        tipo = 'Ação'
        
        rec = info.get('recommendationKey', 'hold').lower()
        perfil_alvo = "Arrojado" if rec in ['strong_buy', 'buy'] else "Moderado"
            
        rend_decimal = info.get('trailingAnnualDividendYield', None)
        rendimento_ultimo_ano = f"{(rend_decimal * 100):.2f}% (Dividendos)" if rend_decimal else "N/A"
            
        valor_minimo = info.get('regularMarketPreviousClose', 0.0)
        prazo_saque = "D+2" 
        banco_corretora = info.get('exchangeName', 'B3')

        sql_insert = """
        INSERT INTO ativos (nome, ticker, tipo, perfil_alvo, rendimento_ultimo_ano, valor_minimo, prazo_saque, banco_corretora)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert, (nome, ticker_simbolo, tipo, perfil_alvo, rendimento_ultimo_ano, valor_minimo, prazo_saque, banco_corretora))
        db.commit()
        
        cursor.execute("SELECT * FROM ativos WHERE ticker = ?", (ticker_simbolo,))
        ativo_novo = cursor.fetchone()
        db.close()
        
        print(f"Ticker {ticker_simbolo} salvo no banco (ID: {ativo_novo['id']}).")
        return ativo_novo

    except Exception as e:
        db.close()
        print(f"Erro no get_or_create_ativo: {e}")
        return None