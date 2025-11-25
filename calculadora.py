import yfinance as yf
import sqlite3
import database
import requests
from datetime import datetime, timedelta

def verificar_api_bcb():
    url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/10?formato=json'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return True
    except Exception:
        return False

def get_preco_historico(ticker_simbolo, data_compra_str):
    ticker_sa = ticker_simbolo + ".SA"
    
    try:
        data_compra = datetime.strptime(data_compra_str, '%Y-%m-%d').date()
        data_seguinte = data_compra + timedelta(days=2)
        
        ticker_data = yf.Ticker(ticker_sa)
        
        hist = ticker_data.history(start=data_compra_str, end=data_seguinte.strftime('%Y-%m-%d'), interval="1d")
        
        if hist.empty:
            return None
            
        return hist['Close'].iloc[0]
        
    except Exception as e:
        print(f"Erro ao buscar preço histórico de {ticker_sa}: {e}")
        return None

def get_dados_cdi(data_inicio_str, data_fim_str):
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        return []

    url_api = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}'
    
    try:
        response = requests.get(url_api)
        response.raise_for_status()
        dados = response.json()
        
        if not dados:
            return []
            
        return dados
    except Exception as e:
        print(f"Erro ao buscar API do BCB: {e}")
        return []

def calcular_pre_fixado(valor_investido, taxa_anual_pc, data_compra_str, data_fim_str):
    try:
        taxa_anual = taxa_anual_pc / 100.0
        taxa_diaria = (1 + taxa_anual) ** (1/252) - 1
        
        data_compra = datetime.strptime(data_compra_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        
        dias_corridos = (data_fim - data_compra).days
        
        if dias_corridos <= 0:
            return valor_investido
            
        valor_final = valor_investido * ((1 + taxa_diaria) ** dias_corridos)
        return valor_final
        
    except Exception as e:
        print(f"Erro ao calcular Pré-Fixado: {e}")
        return valor_investido

def calcular_pos_fixado(valor_investido, percentual_cdi, data_compra_str, data_fim_str):
    dados_cdi = get_dados_cdi(data_compra_str, data_fim_str)
    
    if not dados_cdi:
        return valor_investido
        
    taxa_cdi_pc = percentual_cdi / 100.0
    valor_acumulado = valor_investido
    
    try:
        for dia in dados_cdi:
            taxa_diaria_cdi = float(dia['valor']) / 100.0
            taxa_do_investimento = taxa_diaria_cdi * taxa_cdi_pc
            
            valor_acumulado = valor_acumulado * (1 + taxa_do_investimento)
            
        return valor_acumulado
        
    except Exception as e:
        print(f"Erro no loop de cálculo Pós-Fixado: {e}")
        return valor_investido

def calcular_desempenho_carteira(id_usuario):
    print(f"Calculando desempenho para usuário ID: {id_usuario}")
    
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    sql_join = """
    SELECT 
        posicoes.id, 
        ativos.nome, 
        ativos.ticker,
        posicoes.valor_investido, 
        posicoes.data_compra,
        posicoes.tipo_rendimento,
        posicoes.taxa
    FROM 
        posicoes
    JOIN 
        ativos ON posicoes.id_ativo = ativos.id
    WHERE 
        posicoes.id_usuario = ?
    """
    
    cursor.execute(sql_join, (id_usuario,))
    posicoes_db = cursor.fetchall()
    db.close()
    
    if not posicoes_db:
        return [], 0.0, 0.0, 0.0 

    data_hoje_str = datetime.now().strftime('%Y-%m-%d')
    posicoes_calculadas = []
    total_investido_real = 0.0
    valor_atual_total = 0.0
    
    for item in posicoes_db:
        item_dict = dict(item) 
        
        try:
            data_obj = datetime.strptime(item_dict['data_compra'], '%Y-%m-%d')
            item_dict['data_compra_formatada'] = data_obj.strftime('%d/%m/%Y')
        except Exception:
            item_dict['data_compra_formatada'] = item_dict['data_compra']

        total_investido_real += item_dict['valor_investido']
        
        valor_atual_item = 0.0
        
        if item_dict['ticker']:
            preco_atual_acao = 0.0
            try:
                ticker_sa = item_dict['ticker'] + ".SA"
                ticker_info = yf.Ticker(ticker_sa).info
                preco_atual_acao = ticker_info.get('regularMarketPrice', ticker_info.get('regularMarketPreviousClose', 0.0))
                
                preco_historico_compra = get_preco_historico(item_dict['ticker'], item_dict['data_compra'])
                
                if preco_historico_compra and preco_historico_compra > 0:
                    quantidade_calculada = item_dict['valor_investido'] / preco_historico_compra
                    valor_atual_item = quantidade_calculada * preco_atual_acao
                    item_dict['preco_historico_compra'] = preco_historico_compra
                    item_dict['quantidade_calculada'] = quantidade_calculada
                else:
                    valor_atual_item = item_dict['valor_investido']
                    item_dict['preco_historico_compra'] = 0
                    item_dict['quantidade_calculada'] = 0
                    
            except Exception as e:
                print(f"Erro ao calcular Ação {item_dict['ticker']}: {e}")
                valor_atual_item = item_dict['valor_investido']
            
            item_dict['preco_atual'] = preco_atual_acao

        elif item_dict['tipo_rendimento'] == 'PRE':
            valor_atual_item = calcular_pre_fixado(item_dict['valor_investido'], item_dict['taxa'], item_dict['data_compra'], data_hoje_str)

        elif item_dict['tipo_rendimento'] == 'POS':
            valor_atual_item = calcular_pos_fixado(item_dict['valor_investido'], item_dict['taxa'], item_dict['data_compra'], data_hoje_str)
        
        else:
            valor_atual_item = item_dict['valor_investido']
            
        valor_atual_total += valor_atual_item
        
        item_dict['valor_atual_item'] = valor_atual_item
        item_dict['lucro_prejuizo'] = valor_atual_item - item_dict['valor_investido']
        
        posicoes_calculadas.append(item_dict)

    lucro_prejuizo_total = valor_atual_total - total_investido_real
    
    return posicoes_calculadas, total_investido_real, valor_atual_total, lucro_prejuizo_total