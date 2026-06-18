import requests
from bs4 import BeautifulSoup

def get_nasdaq100_tickers():
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', {'id': 'constituents'})
    
    tickers = []
    if table:
        headers_row = table.find('tr')
        headers_th = [th.text.strip() for th in headers_row.find_all('th')]
        ticker_idx = headers_th.index('Ticker') if 'Ticker' in headers_th else 1
        
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) > ticker_idx:
                ticker = cols[ticker_idx].text.strip()
                tickers.append(ticker)
    
    return tickers

tickers = get_nasdaq100_tickers()
print(f"Found {len(tickers)} tickers: {tickers[:10]}")
