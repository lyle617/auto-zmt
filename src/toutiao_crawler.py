import datetime
import requests
import json
import csv
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add a logger
logger = logging.getLogger(__name__)
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
    max_pages = int(os.getenv('CRAWLER_MAX_PAGES', 0))
    next_max_behot_time = None
    timestamp = int(time.time())

    request_count = 0
    processed_titles = set()
    all_data = []

    while page < max_pages:
        if next_max_behot_time is not None:
            max_behot_time_readable = datetime.datetime.fromtimestamp(next_max_behot_time).strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Processing page {page + 1} of {max_pages}, max_behot_time: {max_behot_time_readable}")
        else:
            logger.info(f"Processing page {page + 1} of {max_pages}, max_behot_time: None")
        if page > 0:
            params['max_behot_time'] = next_max_behot_time
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            break

        if not data.get('data'):
            logger.info("No more data to process")
            break

        filtered_data = [item for item in data['data'] if item.get('source', '') != '央视网']
        all_data.extend(filtered_data)

        behot_times = [item.get('behot_time', float('inf')) for item in data.get('data', [])]
        next_max_behot_time = min(behot_times) if behot_times else None
        if not next_max_behot_time:
            logger.info("No more behot_time to process")
            break

        page += 1
        request_count += 1
        time.sleep(5)
    # Remove duplicates
    unique_data = []
    for item in all_data:
        title = item.get('title', '')
        if title not in processed_titles:
            processed_titles.add(title)
            unique_data.append(item)

    # Process unique data
    process_response({'data': unique_data}, timestamp)

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

    try:
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['title', 'publish_time', 'like_count', 'comment_count', 'media_name', 'source', 'abstract', 'article_url', 'tag', 'is_yaowen', 'article_sub_type']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for item in data['data']:
                title = item.get('title', '')
                publish_time = datetime.datetime.fromtimestamp(int(item.get('publish_time', 0))).strftime('%Y-%m-%d %H:%M')

                if item.get('like_count', 0) > 100 and item.get('comment_count', 0) > 100:
                    if title not in titles_written:
                        titles_written[title] = {
                            'title': title,
                            'publish_time': publish_time,
                            'like_count': item.get('like_count', 0),
                            'comment_count': item.get('comment_count', 0),
                            'media_name': item.get('media_name', ''),
                            'source': item.get('source', ''),
                            'abstract': item.get('abstract', ''),
                            'article_url': item.get('article_url', ''),
                            'tag': item.get('tag', ''),
                            'is_yaowen': item.get('log_pb', {}).get('is_yaowen', ''),
                            'article_sub_type': item.get('article_sub_type', '')
                        }

            for title, row in titles_written.items():
                writer.writerow(row)
            logger.info(f"Wrote {len(titles_written)} articles to {csv_file_path}")
    except Exception as e:
        print(f"Error processing response: {e}")
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
        fieldnames = ['title', 'publish_time', 'like_count', 'comment_count', 'media_name', 'source', 'abstract', 'article_url', 'tag', 'is_yaowen', 'article_sub_type']
        writer = csv.DictWriter(top_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in deduplicated_articles:
            writer.writerow(row)
        logger.info(f"Wrote {len(deduplicated_articles)} articles to {top_articles_path}")

def download_titles():
    top_articles_path = os.path.join('articles', 'top_articles.csv')
    if not os.path.exists(top_articles_path):
        logger.error(f"File {top_articles_path} does not exist.")
        return

    with open(top_articles_path, mode='r', encoding='utf-8') as top_file:
        reader = csv.DictReader(top_file)
        for row in reader:
            article_url = row.get('article_url', '')
            title = row.get('title', '').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            if not article_url or not title:
                logger.warning(f"Skipping article with missing URL or title: {row}")
                continue

            try:
                response = requests.get(article_url, timeout=10)
                response.raise_for_status()
                if not os.path.exists('articles/details'):
                os.makedirs('articles/details')
            with open(os.path.join('articles/details', f'{title}.html'), 'wb') as file:
                    file.write(response.content)
                logger.info(f"Downloaded article: {title}")
                time.sleep(1)
            except requests.RequestException as e:
                logger.error(f"Failed to download article {title}: {e}")

if __name__ == "__main__":
    articles_request()
    download_titles()
