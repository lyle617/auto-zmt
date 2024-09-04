import requests
import json
import csv
import os
import time

def analyze_curl_request():
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
    max_pages = 10
    next_max_behot_time = None
    timestamp = int(time.time())

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

def process_response(response, timestamp):
    data = response
    if not data.get('data'):
        return

    csv_file_path = f'extracted_data_{timestamp}.csv'
    file_exists = os.path.isfile(csv_file_path)

    titles_written = set()

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['title', 'media_name', 'source', 'abstract', 'article_url', 'comment_count', 'like_count', 'share_url', 'publish_time', 'tag']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for item in data['data']:
            title = item.get('title', '')
            if title not in titles_written:
                writer.writerow({
                    'title': title,
                    'media_name': item.get('media_name', ''),
                    'source': item.get('source', ''),
                    'abstract': item.get('abstract', ''),
                    'article_url': item.get('article_url', ''),
                    'comment_count': item.get('comment_count', 0),
                    'like_count': item.get('like_count', 0),
                    'share_url': item.get('share_url', ''),
                    'publish_time': item.get('publish_time', ''),
                    'tag': item.get('tag', '')
                })
                titles_written.add(title)

if __name__ == "__main__":
    analyze_curl_request()