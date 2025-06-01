import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import os

# Global Constants
BASE_URL = 'https://store.steampowered.com/search/results/'
PARAMS_TEMPLATE = {
    'query': '',
    'start': 0,
    'count': 50,
    'dynamic_data': '',
    'sort_by': '_ASC',
    'snr': '1_7_7_7000_7',
    'filter': 'topsellers',
    'tags': '19',
    'infinite': 1
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36'
}


def fetch_results_html(start: int) -> str:
    """Fetch HTML for a page of Steam results."""
    params = PARAMS_TEMPLATE.copy()
    params['start'] = start
    response = requests.get(BASE_URL, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json().get('results_html', '')


def parse_html(html: str) -> list[dict]:
    """Parse game info from HTML."""
    games = []
    soup = BeautifulSoup(html, 'html.parser')

    for item in soup.find_all('a'):
        title_tag = item.find('span', class_='title')
        price_tag = item.find('div', class_='search_price')

        if not title_tag or not price_tag:
            continue

        title = title_tag.text.strip()
        price_parts = price_tag.text.strip().replace('\n', '').split('$')
        price_parts = [p.strip() for p in price_parts if p.strip()]

        try:
            original = float(price_parts[0].replace(",", ""))
            discounted = float(price_parts[1].replace(",", "")) if len(price_parts) > 1 else original
            discount_percent = round((original - discounted) * 100 / original, 0)
        except (IndexError, ValueError):
            continue

        games.append({
            'Title': title,
            'Original Price ($)': f"{original:.2f}",
            'Discounted Price ($)': f"{discounted:.2f}",
            'Discount (%)': f"{discount_percent:.0f}%"
        })

    return games


def get_total_results() -> int:
    """Retrieve total number of games to scrape."""
    response = requests.get(BASE_URL, params=PARAMS_TEMPLATE, headers=HEADERS)
    response.raise_for_status()
    return int(response.json().get('total_count', 0))


def save_as_html(data: list[dict], filename: str):
    """Save game list to a styled HTML file."""
    df = pd.DataFrame(data)
    if df.empty:
        print("⚠️ No games found to save. Exiting.")
        return

    styled = df.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#333'), ('color', 'white')]},
        {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]},
        {'selector': 'tbody tr:hover', 'props': [('background-color', '#ddd')]}
    ])

    os.makedirs("output", exist_ok=True)
    path = os.path.join("output", filename)
    styled.to_html(path, doctype_html=True)
    print(f"\n✅ Output saved as: {path}")


def main():
    print("🎮 Steam Top Sellers Scraper Starting...\n")
    total = get_total_results()
    print(f"📦 Total games to scrape: {total}\n")

    all_games = []
    for start in tqdm(range(0, total, PARAMS_TEMPLATE['count']), desc="Scraping Steam"):
        html = fetch_results_html(start)
        games = parse_html(html)
        # tqdm.write(f"  ➜ {len(games)} games fetched from start={start}")
        all_games.extend(games)

    if not all_games:
        print("❌ No games were parsed. Steam may have blocked the scraper or changed the HTML structure.")
        return

    timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    filename = f"steam_games_{timestamp}.html"
    save_as_html(all_games, filename)


if __name__ == "__main__":
    main()
