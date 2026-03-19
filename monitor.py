import requests
import os
import json


TOKEN_BRAPI = os.getenv('BRAPI_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def carregar_configuracoes():

    with open('config.json', 'r') as f:
        data = json.load(f)
    return {item['ticker']: {'min': item['min'], 'max': item['max']} for item in data['monitoramento']}

def enviar_telegram(mensagem):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensagem, 
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def verificar_carteira():
    hora_atual_utc = datetime.utcnow().hour
    if hora_atual_utc == 13:
        enviar_telegram("🤖 *Monitor de Ações:* Sistema online. O mercado abriu e estou a vigiar os seus ativos!")
    config = carregar_configuracoes()
    tickers_str = ",".join(config.keys())
    
    url = f"https://brapi.dev/api/quote/{tickers_str}?token={TOKEN_BRAPI}"
    
    try:
        response = requests.get(url).json()
        
        for ativo in response.get('results', []):
            ticker = ativo['symbol']
            preco_atual = ativo['regularMarketPrice']
            
            limites = config.get(ticker)
            if not limites: 
                continue

            # Lógica de Alerta para Preço Mínimo
            if preco_atual <= limites['min']:
                msg = (f"⚠️ *ALERTA:* {ticker}\n"
                       f"Preço Atual: *R$ {preco_atual:.2f}*\n"
                       f"Abaixo do limite mínimo: R$ {limites['min']:.2f}")
                enviar_telegram(msg)
            
            # Lógica de Alerta para Preço Máximo
            elif preco_atual >= limites['max']:
                msg = (f"⚠️ *ALERTA:* {ticker}\n"
                       f"Preço Atual: *R$ {preco_atual:.2f}*\n"
                       f"Acima do limite máximo: R$ {limites['max']:.2f}")
                enviar_telegram(msg)
                
    except Exception as e:
        print(f"Erro ao processar ativos: {e}")

if __name__ == "__main__":
    verificar_carteira()
