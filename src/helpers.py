# helpers.py
import requests
from bs4 import BeautifulSoup

def fetch_data(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    # Return the HTML snippet containing the games
    return response.json().get('results_html', '')

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    games = []
    for game in soup.find_all('a'):
        title_elem = game.find('span', class_='title')
        if not title_elem:
            continue  # Skip if title is missing
        title = title_elem.text.strip()

        price_div = game.find('div', class_='search_price')
        if not price_div:
            continue  # Skip if price info is missing
        price_text = price_div.text.strip()
        price_parts = price_text.split('$')
        if len(price_parts) < 2:
            continue  # Not enough pricing info

        original_price = price_parts[1].strip() or '0'
        # If there's a discounted price it will be the third element; otherwise, use the original
        discounted_price = price_parts[2].strip() if len(price_parts) > 2 else original_price

        try:
            original_val = float(original_price.replace(',', ''))
            discounted_val = float(discounted_price.replace(',', ''))
            discount_pct = round((original_val - discounted_val) * 100 / original_val, 0) if original_val else 0
        except ValueError:
            discount_pct = 0

        games.append({
            'Title': title,
            'Original Price': original_price,
            'Discounted Price': discounted_price,
            'Discount (%)': discount_pct
        })
    return games

def get_total_results(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('total_count', 0)
