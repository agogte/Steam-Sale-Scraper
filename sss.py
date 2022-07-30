from turtle import clear
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime

url = 'https://store.steampowered.com/search/results/?query&start=0&count=50&dynamic_data=&force_infinite=1&filter=topsellers&snr=1_7_7_7000_7&infinite=1'

def get_data(url):
    r = requests.get(url)
    data = dict(r.json())
    return data['results_html']


def parse(data):
    gameslist = []
    soup = BeautifulSoup(data, 'html.parser')
    games = soup.find_all('a')
    for game in games:
        title = game.find('span', {'class': 'title'}).text
        price = game.find('div', {'class': 'search_price'}).text.strip().split('$')[1]
        try:
            discprice = game.find('div', {'class': 'search_price'}).text.strip().split('$')[2]
        except:
            discprice = price
        #print(title,price, discprice)

        mygame ={
            'Title': title,
            'Original Price': price,
            'Discounted Price': discprice,
            'Discount (in %)': round((float(price.replace(",", "")) - float(discprice.replace(",", "")))*100/float(price.replace(",", "")),0)
        }
        gameslist.append(mygame)
    return gameslist

now = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

def output(results):
    gamesdf = pd.concat([pd.DataFrame(g) for g in results])
    gamesdf.to_csv(f'gamesprices_{now}.csv', index=False)
    print(f'Done.\nSaved as gamesprices_{now}.csv')
    #print(gamesdf.head())
    return

results = []

def total_results(url):
    r = requests.get(url)
    data = dict(r.json())
    totalresults = data['total_count']
    return int(totalresults)

for x in range(0, total_results(url), 50):
    data = get_data(f'https://store.steampowered.com/search/results/?query&start={x}&count=50&dynamic_data=&sort_by=_ASC&snr=1_7_7_7000_7&filter=topsellers&tags=19&infinite=1')
    results.append(parse(data))
    print('Results Scraped: ', x)


output(results)
