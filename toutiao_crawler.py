import requests
import json
import csv
import os
import time

def articles_request():
    base_url = 'https://m.toutiao.com/list/'
    params = {
        'tag': '__all__',
        'max_time': '1725409291',
        'ac': 'wap',
        'count': '20',
        'format': 'json_raw',
        '_signature': 'oxib-wAAxdpfXCDdxPIW2KMYm-',
        'i': '1725409291',
        'as': 'A116960D97ABEFA',
        'cp': '66D7EB3EAFCA6E1',
        'aid': '1698'
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': os.getenv('CRAWLER_COOKIE'),
        'Pragma': 'no-cache',
        'Referer': 'https://m.toutiao.com/?&source=m_redirect',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"'
    }

    page = 0
    max_pages = 100
    next_max_behot_time = None
    timestamp = int(time.time())

    request_count = 0
    while page < max_pages:
        if page == 0:
            response = requests.get(base_url, headers=headers, params=params)
        else:
            params['max_behot_time'] = next_max_behot_time
            response = requests.get(base_url, headers=headers, params=params)

        data = response.json()

        if not data.get('data'):
            break

        process_response(data, timestamp)
        output_data = {
            "response": response.text,
            "max_behot_time": next_max_behot_time
        }
        print(json.dumps(output_data, ensure_ascii=False, indent=4))

        behot_times = [item.get('behot_time', float('inf')) for item in data.get('data', [])]
        next_max_behot_time = min(behot_times) if behot_times else None
        if not next_max_behot_time:
            break

        page += 1
        request_count += 1
        if request_count % 10 == 0:
            time.sleep(2)

def process_response(response, timestamp):
    data = response
    if not data.get('data'):
        return

    if not os.path.exists('articles'):
        os.makedirs('articles')
    csv_file_path = os.path.join('articles', f'extracted_data_{timestamp}.csv')
    top_articles_path = os.path.join('articles', 'top_articles.csv')
    file_exists = os.path.isfile(csv_file_path)

    titles_written = {}

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['title', 'media_name', 'source', 'abstract', 'article_url', 'comment_count', 'like_count', 'share_count', 'share_url', 'publish_time', 'tag', 'read_count', 'is_yaowen', 'article_sub_type']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for item in data['data']:
            title = item.get('title', '')
            from datetime import datetime
            publish_time = datetime.fromtimestamp(int(item.get('publish_time', 0))).strftime('%Y-%m-%d %H:%M')

            if item.get('like_count', 0) > 100 and item.get('comment_count', 0) > 100:
                if title not in titles_written or publish_time >= titles_written[title]['publish_time']:
                    titles_written[title] = {
                        'title': title,
                        'media_name': item.get('media_name', ''),
                        'source': item.get('source', ''),
                        'abstract': item.get('abstract', ''),
                        'article_url': item.get('article_url', ''),
                        'comment_count': item.get('comment_count', 0),
                        'like_count': item.get('like_count', 0),
                        'publish_time': publish_time,
                        'tag': item.get('tag', ''),
                        'is_yaowen': item.get('log_pb', {}).get('is_yaowen', ''),
                        'article_sub_type': item.get('article_sub_type', '')
                    }

        for title, row in titles_written.items():
            writer.writerow({
                'title': row['title'],
                'media_name': row['media_name'],
                'source': row['source'],
                'abstract': row['abstract'],
                'article_url': row['article_url'],
                'comment_count': row['comment_count'],
                'like_count': row['like_count'],
                'publish_time': row['publish_time'],
                'tag': row['tag'],
                'is_yaowen': row['is_yaowen'],
                'article_sub_type': row['article_sub_type']
            })

    # Merge with top_articles.csv and sort by like_count
    top_articles = []
    if os.path.exists(top_articles_path):
        with open(top_articles_path, mode='r', encoding='utf-8') as top_file:
            reader = csv.DictReader(top_file)
            top_articles = list(reader)

    unique_titles = set()
    deduplicated_articles = []

    for title, row in titles_written.items():
        if title not in unique_titles:
            unique_titles.add(title)
            deduplicated_articles.append(row)

    for article in top_articles:
        if article['title'] not in unique_titles:
            unique_titles.add(article['title'])
            deduplicated_articles.append(article)

    deduplicated_articles = sorted(deduplicated_articles, key=lambda x: int(x['like_count']), reverse=True)[:500]

    with open(top_articles_path, mode='w', newline='', encoding='utf-8') as top_file:
        fieldnames = ['title', 'media_name', 'source', 'abstract', 'article_url', 'comment_count', 'like_count', 'publish_time', 'tag', 'is_yaowen', 'article_sub_type']
        writer = csv.DictWriter(top_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in deduplicated_articles:
            writer.writerow(row)

if __name__ == "__main__":
    articles_request()