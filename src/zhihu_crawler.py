
import random
import time
import requests
import json
import os
import logging

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

    def get_answers(self, question_id, order='updated', limit=20):
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

        while not is_end:
            logging.info(f"Fetching page {page + 1} for question ID: {question_id}")
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                logging.info(f"Successfully fetched answers for question ID: {question_id}")
            except requests.RequestException as e:
                logging.error(f"Failed to fetch answers for question ID: {question_id}. Error: {e}")
                break

            all_answers.extend(data.get('data', []))
            is_end = data['paging']['is_end']
            url = data['paging']['next']
            page += 1
            sleep_time = random.uniform(1, 5)  # Random sleep time between 1 and 2 seconds
            time.sleep(sleep_time)  # Add a delay to avoid rate limiting

        return all_answers

if __name__ == "__main__":
    cookie = "_xsrf=y8SqpKJbgHYnf0fqO36v8ZrTNApYNFe9; _zap=1e1966a1-bd6b-4a18-ba2e-1b699074eb91; d_c0=ANAVibVE_xePTmSODk-7qa7b9DX_DnJn1hk=|1705047763; __snaker__id=QVQHFx5ySDwFekqR; q_c1=b85740d1757d4d74bf04e7e3f43cc5bc|1705369475000|1705369475000; q_c1=b85740d1757d4d74bf04e7e3f43cc5bc|1725965099000|1705369475000; HMACCOUNT=5C1E600B38DAB84E; z_c0=2|1:0|10:1727350649|4:z_c0|80:MS4xaHZTYUF3QUFBQUFtQUFBQVlBSlZUWDl2eldkOHpzdWgydHFkNE9vQ1pXaV8wV0dtQnUwVS1BPT0=|9916518dffc53e9b4f43ce13c2f34cd282e2e8d76137b0bc084fe5f5f667f15c; tst=h; SESSIONID=u5bnXP5jYBDxg6M87bbcoAFa1LQYckDPETuR5GuS7JG; JOID=Vl0cAEkiE3QcQRUOcCVUq-IllRxkVioccx9ENxB9UDxuJyVCRN2BiX1GGAh70M_pSHjo9V8bH2se48rr8FJ00e4=; osd=V1gVAUojFn0dQhQLeSRXqucslB9lUyMdcB5BPhF-UTlnJiZDQdSAinxDEQl40crgSXvp8FYaHGob6svo8Vd90O0=; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1727349902; __zse_ck=003_bvEOmZWPtbsKPCsKp+qHe4OROj4vqRu4La/2w9mSga6PJmJtJC74yxShaUy9uWwZ7TPk9HvzYop47b7Qx7TuqMHOwwGM+QqRT6CN58JUsKe2; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1727436021; BEC=6ff32b60f55255af78892ba1e551063a"
    crawler = zhihuCrawler(cookie=cookie)
    answers = crawler.get_answers('668753879')
    if answers:
        for answer in answers:
            print(json.dumps(answer, indent=2, ensure_ascii=False))