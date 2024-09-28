
import random
import time
import requests
import json
import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class zhihuCrawler:
    def __init__(self, cookie):
        self.base_url = 'https://www.zhihu.com/api/v4'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            'cookie': cookie,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }

    def save_answers(self, answers, question_id):
        import csv
        import os

        output_dir = 'zhihu_result'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_path = os.path.join(output_dir, f'{question_id}.csv')
        file_exists = os.path.exists(file_path)
        mode = 'w' if file_exists else 'x'
        with open(file_path, mode=mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Author ID', 'Author Nickname', 'Author Type', 'Author Headline', 'Likes Count', 'Thanks Count', 'Comment Count', 'Content'])
            for answer in answers:
                target = answer.get('target', {})
                author = target.get('author', {})
                content = target.get('content', '')
                content = re.sub('<.*?>', '', content)
                logging.info(f"Writing answer to CSV: Author ID: {author.get('id')}, Author Nickname: {author.get('name')}, Author Type: {author.get('type')}, Author Headline: {author.get('headline')}, Vote-up Count: {target.get('voteup_count')}, Thanks Count: {target.get('thanks_count')}, Comment Count: {target.get('comment_count')}, Content: {content}")
                writer.writerow([author.get('id'), author.get('name'), author.get('type'), author.get('headline'), target.get('voteup_count'), target.get('thanks_count'), target.get('comment_count'), content])
                logging.info(f"Successfully wrote answer to CSV: Author ID: {author.get('id')}")

    def get_answers(self, question_id, order='updated', limit=20, max_pages=3):
        url = f'{self.base_url}/questions/{question_id}/feeds'
        logging.info(f"Sending request to URL: {url}")
        params = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,attachment,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,is_labeled,paid_info,paid_info_content,reaction_instruction,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].author.follower_count,vip_info,badge[*].topics;data[*].settings.table_of_content.enabled',
            'order': order,
            'limit': limit
        }

        all_answers = []
        is_end = False
        page = 0

        while not is_end and page < max_pages:
            logging.info(f"Fetching page {page + 1} for question ID: {question_id}")
            sleep_time = random.uniform(1, 5)  # Random sleep time between 1 and 2 seconds
            time.sleep(sleep_time)  # Add a delay to avoid rate limiting
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                logging.info(f"Successfully fetched answers for question ID: {question_id}. Sleeping for {sleep_time:.2f} seconds.")
            except requests.RequestException as e:
                logging.error(f"Failed to fetch answers for question ID: {question_id}. Error: {e}")
                break

            for answer in data.get('data', []):
                target = answer.get('target', {})
                author = target.get('author', {})
                content = target.get('content', {})
                content = re.sub('<.*?>', '', content)
                # logging.info(f"answer: {json.dumps(answer, indent=2, ensure_ascii=False)}") 
                logging.info(f"Author ID: {author.get('id')}, Author Nickname: {author.get('name')}, Author Type: {author.get('type')}, Author Headline: {author.get('headline')}, Vote-up Count: {target.get('voteup_count')}, Thanks Count: {target.get('thanks_count')}, Comment Count: {target.get('comment_count')}, Content: {content}")

            all_answers.extend(data.get('data', []))
            is_end = data['paging']['is_end']
            url = data['paging']['next']
            page += 1

        return all_answers

import os

if __name__ == "__main__":
    cookie = os.getenv('ZHIHU_COOKIE')
    if not cookie:
        raise ValueError("ZHIHU_COOKIE environment variable is not set")

    questions_id = os.getenv('ZHIHU_QUESTION_ID')
    if not questions_id:
        raise ValueError("ZHIHU_QUESTION_ID environment variable is not set")

    max_pages = int(os.getenv('ZHIHU_MAX_PAGES', '3'))

    crawler = zhihuCrawler(cookie=cookie)
    answers = crawler.get_answers(question_id=questions_id, max_pages=max_pages, order='')
    crawler.save_answers(answers, questions_id)