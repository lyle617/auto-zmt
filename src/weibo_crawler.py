import requests
import json
import csv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the common comments directory
import os

SAVE_DIR = 'weibo_results'

def fetch_weibo_comments(id, max_id=None):
    base_url = 'https://m.weibo.cn/comments/hotflow'
    params = {
        'id': id,
        'mid': id,
        'max_id_type': 0
    }
    if max_id is not None:
        params['max_id'] = max_id

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'cookie': 'WEIBOCN_FROM=1110006030; _T_WM=76640575475; SCF=AuIlz2ZhZeGfr-nzWary7cNSnUvss9hXdXGcX8GxbOm3JMCMl-en38dhOk0nEhLpNI6dAEOS8aU2Lu-SfAZaNmE.; SUB=_2A25L2qMIDeRhGedI7FEZ9C3LzzyIHXVombrArDV6PUJbktAGLWXHkW1NVtqVtztQwix2KdMiQYl5HT4mKz4mj_Od; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWau3EFDRIdmcTh_LopJe1p5NHD95QpSoM01hB0S0B7Ws4Dqcji9J9J9LvAwrDA; SSOLoginState=1725879130; ALF=1728471130; MLOGIN=1; XSRF-TOKEN=7e0233; mweibo_short_token=e55b1095e9; M_WEIBOCN_PARAMS=luicode%3D20000174%26oid%3D5076707294580158%26lfid%3D5076707294580158%26uicode%3D10000011%26fid%3D100103type%253D1%2526t%253D10%2526q%253D%25E5%25B0%258F%25E6%259D%25A8%25E5%2593%25A5%2B%25E7%25A3%25A8%25E9%25AA%25A8',
        'mweibo-pwa': '1',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://m.weibo.cn/detail/{id}',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': '93b999'
    }

    url = f"{base_url}?id={params['id']}&mid={params['mid']}&max_id_type={params['max_id_type']}"
    if 'max_id' in params:
        url += f"&max_id={params['max_id']}"
    logging.info("Fetching comments from URL: %s", url)
    response = requests.get(url, headers=headers)
    import time
    time.sleep(1)
    if response.status_code == 200:
        logging.info("API call successful")
        # logging.info("Response result: %s", response.text)
        return response.json()
    else:
        logging.error("API call failed with status code: %s", response.status_code)
        return None

import re

def strip_html_tags(text):
    """Remove all HTML tags from the given text."""
    return re.sub(r'<.*?>', '', text)

def save_comments_to_csv(comments, file_path):

    existing_comments = set()
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                existing_comments.add(row['id'])

    with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['id', 'text', 'user_id', 'user_name', 'created_at', 'likes', 'reply_to_id', 'reply_to_text']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if csv_file.tell() == 0:
            writer.writeheader()

        new_comments = 0
        duplicate_comments = 0
        for comment in comments:
            comment_id = comment.get('id', '')
            if comment_id not in existing_comments:
                cleaned_text = strip_html_tags(comment.get('text', ''))
                reply_to_id = comment.get('reply_to_comment_id', '')
                reply_to_text = strip_html_tags(comment.get('reply_to_comment_text', ''))
                writer.writerow({
                    'id': comment_id,
                    'text': cleaned_text,
                    'user_id': comment.get('user', {}).get('id', ''),
                    'user_name': comment.get('user', {}).get('screen_name', ''),
                    'created_at': comment.get('created_at', ''),
                    'likes': comment.get('like_count', 0),
                    'reply_to_id': reply_to_id,
                    'reply_to_text': reply_to_text
                })
                new_comments += 1
            else:
                duplicate_comments += 1
        logging.info("Saved %d new comments to %s", new_comments, file_path)
        logging.info("Skipped %d duplicate comments", duplicate_comments)

def fetch_weibo_detail(id):
    base_url = 'https://m.weibo.cn/statuses/extend'
    params = {
        'id': id
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'cookie': 'WEIBOCN_FROM=1110006030; SCF=AuIlz2ZhZeGfr-nzWary7cNSnUvss9hXdXGcX8GxbOm3JMCMl-en38dhOk0nEhLpNI6dAEOS8aU2Lu-SfAZaNmE.; SUB=_2A25L2qMIDeRhGedI7FEZ9C3LzzyIHXVombrArDV6PUJbktAGLWXHkW1NVtqVtztQwix2KdMiQYl5HT4mKz4mj_Od; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWau3EFDRIdmcTh_LopJe1p5NHD95QpSoM01hB0S0B7Ws4Dqcji9J9J9LvAwrDA; SSOLoginState=1725879130; ALF=1728471130; _T_WM=35112945113; MLOGIN=1; XSRF-TOKEN=dbcb5c; mweibo_short_token=2b96126c6c; M_WEIBOCN_PARAMS=oid%3D5076707294580158%26luicode%3D20000061%26lfid%3D5076707294580158%26uicode%3D20000061%26fid%3D5076707294580158',
        'mweibo-pwa': '1',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://m.weibo.cn/detail/{id}',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    url = f"{base_url}?id={params['id']}"
    logging.info("Fetching detail from URL: %s", url)
    response = requests.get(url, headers=headers)
    import time
    time.sleep(1)
    if response.status_code == 200:
        logging.info("API call successful")
        long_text_content = response.json().get('data', {}).get('longTextContent', None)
        if long_text_content:
            long_text_content = strip_html_tags(long_text_content)
        return long_text_content
    else:
        logging.error("API call failed with status code: %s", response.status_code)
        return None

def crawl_weibo_comments(id):
    max_id = None
    while True:
        response = fetch_weibo_comments(id, max_id)
        if not response:
            logging.info("Terminating due to empty response")
            break
        if not response.get('data', {}).get('data'):
            logging.info("Terminating due to empty data in response")
            break

        comments = response['data']['data']
        save_comments_to_csv(comments, os.path.join(SAVE_DIR, f'weibo_comments_{id}.csv'))

        max_id = response['data'].get('max_id')
        if not max_id:
            logging.info("Terminating due to no more max_id")
            break

def crawl_weibo_detail(id):
    detail = fetch_weibo_detail(id)
    if detail:
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
        file_path = os.path.join(SAVE_DIR, f'weibo_detail_{id}.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(detail)
        logging.info("Saved Weibo detail to %s", file_path)
    else:
        logging.error("Failed to fetch Weibo detail for id: %s", id)

if __name__ == "__main__":
    logging.info("Starting Weibo crawler")
    crawl_weibo_detail('5076707294580158')
    crawl_weibo_comments('5076707294580158')