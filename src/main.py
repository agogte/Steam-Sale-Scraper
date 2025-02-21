from datetime import datetime
import pandas as pd
from .config import BASE_URL, PARAMS
from .helpers import fetch_data, parse, get_total_results
from tqdm import tqdm

def save_to_csv(games):
    df = pd.DataFrame(games)
    timestamp = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    filename = f'gamesprices_{timestamp}.csv'
    df.to_csv(filename, index=False)
    print(f"Done. Saved as {filename}")

def main():
    total = get_total_results(BASE_URL, PARAMS)
    print("Total results:", total)
    all_games = []
    # Using tqdm to create a loading bar
    for start in tqdm(range(0, total, PARAMS['count']), desc="Scraping results"):
        PARAMS['start'] = start
        html = fetch_data(BASE_URL, PARAMS)
        games = parse(html)
        all_games.extend(games)
    save_to_csv(all_games)

if __name__ == '__main__':
    main()
