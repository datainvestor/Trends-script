import requests
from bs4 import BeautifulSoup
import datetime
import time
import os
import logging
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Configuration
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

def send_notification(message):
    try:
        logging.info(f"Sending notification to topic: {NTFY_TOPIC} ({NTFY_URL})")
        requests.post(NTFY_URL, data=message.encode(encoding='utf-8'))
        logging.info("Notification sent!")
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")

def get_twitter_trends(url, name):
    try:
        logging.info(f"Fetching {name} trends...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            trend_list = soup.select('#trend-list .trend-card__list')
            if not trend_list:
                trend_list = soup.select('.trend-card__list')
            
            if trend_list:
                latest_trends = trend_list[0].find_all('li')
                trends = [t.get_text(strip=True) for t in latest_trends[:15]]
                return " ,".join(trends)
    except Exception as e:
        logging.error(f"Error fetching {name} trends: {e}")
    return "N/A"

def get_yahoo_trends():
    try:
        logging.info("Fetching Yahoo Trends...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = requests.get("https://finance.yahoo.com/trending-tickers/", headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        # New selector found via inspection
        base = soup.select('a[data-testid="table-cell-ticker"]')
        
        return " ,".join(x.get_text(strip=True) for x in base[0:15])
    except Exception as e:
        logging.error(f"Error fetching Yahoo Trends: {e}")
        return "N/A"

def get_crypto_trends():
    try:
        logging.info("Fetching Crypto Trends...")
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': 'false'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            top_coins = data
            top_coins.sort(key=lambda x: x['price_change_percentage_24h'] or 0, reverse=True)
            
            cmcstr = ' ,'.join([f"{c['symbol'].upper()}: {c['price_change_percentage_24h']}%" for c in top_coins[:5]])
            return cmcstr
    except Exception as e:
        logging.error(f"Error fetching Crypto Trends: {e}")
    return "N/A"

def main():
    now = datetime.datetime.now()
    logging.info(f"Running trends script at {now}")

    # Polish Trends
    strPLT = get_twitter_trends("https://trends24.in/poland/", "Poland")
    
    # Global Trends
    strGT = get_twitter_trends("https://trends24.in/", "Global")
    
    # Yahoo Trends
    strYHOO = get_yahoo_trends()
    
    # Crypto Trends
    cmcstr = get_crypto_trends()

    # Construct Message
    message = (
        f"***TREND TWT POLSKA: {strPLT}\n"
        f"***TREND TWT GLOBAL: {strGT}\n"
        f"***TOP TICKERS YAHOO: {strYHOO}\n"
        f"***CMC TOP: {cmcstr}"
    )
    
    logging.info("Sending Notification...")
    send_notification(message)
    logging.info("Done.")

if __name__ == "__main__":
    main()
