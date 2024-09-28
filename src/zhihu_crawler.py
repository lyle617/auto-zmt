
import requests
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class zhihuCrawler:
    def __init__(self):
        self.base_url = 'https://www.zhihu.com/api/v4/questions/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            'Authorization': f'Bearer {os.getenv("ZHIHU_TOKEN")}'
        }

    def get_answers(self, question_id):
        url = f'{self.base_url}{question_id}/answers'
        params = {
            'include': 'data[*].content,voteup_count,comment_count,author.badge[?(type=best_answerer)].topics',
            'limit': 20,
            'offset': 0
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            logging.info(f"Successfully fetched answers for question ID: {question_id}")
            return data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch answers for question ID: {question_id}. Error: {e}")
            return None

if __name__ == "__main__":
    crawler = zhihuCrawler()
    answers = crawler.get_answers('29292929')
    if answers:
        print(json.dumps(answers, indent=2, ensure_ascii=False))