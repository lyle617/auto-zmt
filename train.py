import requests
import csv
import os

def deepseek_api_call(titles):
    api_url = "https://api.deepseek.com/v1/models"
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    }
    data = {
        'titles': titles
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        print("API call successful")
        print(response.json())
    else:
        print("API call failed with status code:", response.status_code)

def read_titles_from_csv(file_path):
    titles = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            titles.append(row['title'])
    return titles

if __name__ == "__main__":
    csv_file_path = os.path.join('articles', 'top_articles.csv')
    titles = read_titles_from_csv(csv_file_path)
    deepseek_api_call(titles)