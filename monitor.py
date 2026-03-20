import requests
import os
import json
from datetime import datetime

TOKEN_BRAPI = os.getenv('BRAPI_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def carregar_configuracoes():
    try:
        with open('config.json', 'r') as f:
            data = json.load(f)
     
        return data.get('monitoramento', [])
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        return []

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def verificar_carteira():
    regras = carregar_configuracoes()
    
    # Mensagem de Status (10h-11h BRT)
    hora_utc = datetime.utcnow().hour
    if hora_utc in [13, 14]:
        enviar_telegram("🤖 *Monitor de Ações:* Sistema online e vigiando o pregão!")

    if not regras:
        print("Nenhuma regra configurada.")
        return 

   
    tickers_unicos = list(set([item['ticker'] for item in regras]))
    tickers_str = ",".join(tickers_unicos)
    
    url = f"https://brapi.dev/api/quote/{tickers_str}?token={TOKEN_BRAPI}"
    
    try:
        response = requests.get(url).json()
     
        precos_mercado = {ativo['symbol']: ativo.get('regularMarketPrice') for ativo in response.get('results', [])}

   
        for regra in regras:
            ticker = regra['ticker']
            preco_atual = precos_mercado.get(ticker)
            
            if preco_atual is None: continue

           
            if preco_atual <= regra['min']:
                enviar_telegram(f"⚠️ *ALERTA (Mín):* {ticker}\nPreço: *R$ {preco_atual:.2f}*\nAlvo: R$ {regra['min']:.2f}")
            elif preco_atual >= regra['max']:
                enviar_telegram(f"⚠️ *ALERTA (Máx):* {ticker}\nPreço: *R$ {preco_atual:.2f}*\nAlvo: R$ {regra['max']:.2f}")
                
    except Exception as e:
        print(f"Erro na API: {e}")

if __name__ == "__main__":
    verificar_carteira()
