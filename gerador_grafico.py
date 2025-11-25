import matplotlib.pyplot as plt
import yfinance as yf
import os
import datetime

def gerar_grafico_anual(ticker_simbolo):
    if not ticker_simbolo:
        return None

    ticker_completo = ticker_simbolo.upper() + ".SA"
    
    try:
        data = yf.Ticker(ticker_completo).history(period="1y")
        
        if data.empty:
            return None
        
        timestamp = datetime.datetime.now().strftime("%H.%M.%S-%d.%m.%Y")
        nome_arquivo_novo = f"{ticker_simbolo}_{timestamp}.png"
        charts_dir = os.path.join('static', 'charts')
        caminho_salvar = os.path.join(charts_dir, nome_arquivo_novo)
        caminho_relativo = f'charts/{nome_arquivo_novo}'

        plt.figure(figsize=(10, 5))
        plt.plot(data['Close'])
        plt.title(f'Desempenho de {ticker_simbolo} (Último Ano)')
        plt.ylabel('Preço de Fechamento (R$)')
        plt.xlabel('Data')
        plt.grid(True)
        
        plt.savefig(caminho_salvar)
        plt.close() 

        for filename in os.listdir(charts_dir):

            if filename.startswith(f"{ticker_simbolo}_") and filename != nome_arquivo_novo:
                try:
                    os.remove(os.path.join(charts_dir, filename))
                except Exception as e:
                    print(f"Erro ao deletar gráfico antigo {filename}: {e}")
        
        return caminho_relativo

    except Exception as e:
        print(f"Erro ao gerar gráfico para {ticker_simbolo}: {e}")
        return None