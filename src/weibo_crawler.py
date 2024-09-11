import requests
import json
import csv
import os
import logging
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WeiboCrawler:
    SAVE_DIR = 'weibo_results'

    def __init__(self):
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)

    def fetch_weibo_comments(self, id, max_id=None):
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
            'cookie': os.getenv('WEIBO_COOKIE'),
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
        logging.info("Response: %s", response.text)
        time.sleep(1)
        if response.status_code == 200:
            logging.info("API call successful")
            return response.json()
        else:
            logging.error("API call failed with status code: %s", response.status_code)
            return None

    @staticmethod
    def strip_html_tags(text):
        """Remove all HTML tags from the given text."""
        return re.sub(r'<.*?>', '', text)

    def save_comments_to_csv(self, comments, file_path):
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
                    cleaned_text = self.strip_html_tags(comment.get('text', ''))
                    reply_to_id = comment.get('reply_to_comment_id', '')
                    reply_to_text = self.strip_html_tags(comment.get('reply_to_comment_text', ''))
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

    def fetch_weibo_detail(self, id):
        base_url = 'https://m.weibo.cn/statuses/extend'
        params = {
            'id': id
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'cookie': os.getenv('WEIBO_COOKIE'),
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
        time.sleep(1)
        if response.status_code == 200:
            logging.info("API call successful")
            long_text_content = response.json().get('data', {}).get('longTextContent', None)
            if long_text_content:
                long_text_content = self.strip_html_tags(long_text_content)
            return long_text_content
        else:
            logging.error("API call failed with status code: %s", response.status_code)
            return None

    def crawl_weibo_comments(self, id):
        all_comments = []
        max_id = None
        while True:
            response = self.fetch_weibo_comments(id, max_id)
            if not response:
                logging.info("Terminating due to empty response")
                break
            if not response.get('data', {}).get('data'):
                logging.info("Terminating due to empty data in response")
                break

            comments = response['data']['data']
            filtered_comments = [{'likes': comment.get('like_count', 0), 'text': self.strip_html_tags(comment.get('text', ''))} for comment in comments]
            all_comments.extend(filtered_comments)
            self.save_comments_to_csv(comments, os.path.join(self.SAVE_DIR, f'weibo_comments_{id}.csv'))

            max_id = response['data'].get('max_id')
            logging.info("Next max_id: %s", max_id)
            if not max_id:
                logging.info("Terminating due to no more max_id")
                break
        all_comments.sort(key=lambda x: x['likes'], reverse=True)
        return all_comments

    def crawl_weibo_detail(self, id):
        detail = self.fetch_weibo_detail(id)
        if detail:
            file_path = os.path.join(self.SAVE_DIR, f'weibo_detail_{id}.txt')
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(detail)
            logging.info("Saved Weibo detail to %s", file_path)
            return detail
        else:
            logging.error("Failed to fetch Weibo detail for id: %s", id)
            return None

def main():
    logging.info("Starting Weibo crawler")
    crawler = WeiboCrawler()
    detail = crawler.crawl_weibo_detail('5077429968700123')
    comments = crawler.crawl_weibo_comments('5077429968700123')
    if detail:
        print("Weibo Detail:")
        print(detail)
    else:
        print("Failed to fetch Weibo detail.")
    if comments:
        print("Weibo Comments:")
        for comment in comments:
            print(comment)
    else:
        print("Failed to fetch Weibo comments.")

if __name__ == "__main__":
    main()