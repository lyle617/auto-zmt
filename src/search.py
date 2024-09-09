import requests
import csv
import os

def fetch_weibo_hot_search():
    url = "https://weibo.com/ajax/side/hotSearch"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if not os.path.exists('weibo_hot_search'):
        os.makedirs('weibo_hot_search')

    csv_file_path = os.path.join('weibo_hot_search', 'hot_search.csv')

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['rank', 'note', 'category', 'num']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for item in data.get('data', {}).get('realtime', []):
            writer.writerow({
                'rank': item.get('rank'),
                'note': item.get('note'),
                'category': item.get('category'),
                'num': item.get('num')
            })

if __name__ == "__main__":
    fetch_weibo_hot_search()