import csv
import sys
import os

NOME_ARQUIVO_CSV = os.path.join('static', 'B3_ativos.csv')

def buscar_ticker_por_nome(nome_pesquisa):
    nome_pesquisa = nome_pesquisa.strip().lower()
    if not nome_pesquisa:
        return []
    
    encontrados = []
    
    try:
        with open(NOME_ARQUIVO_CSV, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=',') 
            next(reader, None)
            
            for row in reader:
                try:
                    ticker = row[0].strip()
                    nome_oficial = row[1].strip().lower()
                    
                    if nome_pesquisa in nome_oficial:
                        encontrados.append( (ticker, nome_oficial.title()) )
                        
                except IndexError:
                    pass 
        
        return encontrados

    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{NOME_ARQUIVO_CSV}' não encontrado!")
        return []
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao ler o arquivo: {e}")
        return []

def get_todos_os_tickers():
    todos_tickers = []
    
    try:
        with open(NOME_ARQUIVO_CSV, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=',') 
            next(reader, None)
            
            for row in reader:
                try:
                    ticker = row[0].strip()
                    nome_oficial = row[1].strip().title()
                    
                    if ticker and nome_oficial:
                        todos_tickers.append( (ticker, nome_oficial) )
                        
                except IndexError:
                    pass
        
        return todos_tickers

    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{NOME_ARQUIVO_CSV}' não encontrado!")
        return []
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao ler o arquivo: {e}")
        return []