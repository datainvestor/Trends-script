import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import datetime
import time
import os

# Configuration
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

def send_notification(message):
    try:
        requests.post(NTFY_URL, data=message.encode(encoding='utf-8'))
        print("Notification sent!")
    except Exception as e:
        print(f"Failed to send notification: {e}")

def get_twitter_trends(url, name):
    try:
        print(f"Fetching {name} trends...")
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
        print(f"Error fetching {name} trends: {e}")
    return "N/A"

def get_google_trends():
    try:
        print("Fetching Google Trends...")
        pytrends = TrendReq(geo='GB-ENG', tz=360) # Keeping original settings
        df = pytrends.trending_searches()
        gtrendsus = df.iloc[:, 0].tolist() # df.title might be deprecated, using iloc
        return " ,".join(str(x) for x in gtrendsus[0:15])
    except Exception as e:
        print(f"Error fetching Google Trends: {e}")
        return "N/A"

def get_yahoo_trends():
    try:
        print("Fetching Yahoo Trends...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = requests.get("https://finance.yahoo.com/trending-tickers/", headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        # Original selector, might need update but keeping for now
        base = soup.findAll('td', {'class': 'data-col1'}) 
        if not base:
             # Try a more generic selector if specific class fails
             base = soup.select('td[aria-label="Symbol"]')
        
        yhoo = []
        for i in base:
            yhoo.append(i.get_text())
        return " ,".join(str(x) for x in yhoo[0:15])
    except Exception as e:
        print(f"Error fetching Yahoo Trends: {e}")
        return "N/A"

def get_crypto_trends():
    try:
        print("Fetching Crypto Trends...")
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
            # Sort by change? Original script sorted by change.
            # Let's just take top 5 by market cap and show their change
            # Or we can fetch more and sort by change.
            # Original: fetched all, sorted by change.
            # CoinGecko has rate limits, so let's just fetch top 20 and sort.
            
            top_coins = data
            # Sort by percent change descending
            top_coins.sort(key=lambda x: x['price_change_percentage_24h'] or 0, reverse=True)
            
            cmcstr = ' ,'.join([f"{c['symbol'].upper()}: {c['price_change_percentage_24h']}%" for c in top_coins[:5]])
            return cmcstr
    except Exception as e:
        print(f"Error fetching Crypto Trends: {e}")
    return "N/A"

def main():
    now = datetime.datetime.now()
    # Run logic (removed the hour check for testing/manual run, 
    # but for cron we might want it. 
    # Actually, GitHub Actions handles the schedule, so we can remove the hour check 
    # to allow the script to run whenever the action triggers it.)
    
    print(f"Running trends script at {now}")

    # Polish Trends
    strPLT = get_twitter_trends("https://trends24.in/poland/", "Poland")
    
    # Global Trends
    strGT = get_twitter_trends("https://trends24.in/", "Global")
    
    # Google Trends
    strGog = get_google_trends()
    
    # Yahoo Trends
    strYHOO = get_yahoo_trends()
    
    # Crypto Trends
    cmcstr = get_crypto_trends()

    # Construct Message
    message = (
        f"***TREND TWT POLSKA: {strPLT}\n"
        f"***TREND TWT GLOBAL: {strGT}\n"
        f"***G US SEARCH: {strGog}\n"
        f"***TOP TICKERS YAHOO: {strYHOO}\n"
        f"***CMC TOP: {cmcstr}"
    )
    
    print("Sending Notification...")
    send_notification(message)
    print("Done.")

if __name__ == "__main__":
    main()
