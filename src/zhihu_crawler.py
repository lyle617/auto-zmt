
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
        url = f'{self.base_url}{question_id}/feeds'
        params = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,attachment,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,is_labeled,paid_info,paid_info_content,reaction_instruction,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].author.follower_count,vip_info,badge[*].topics;data[*].settings.table_of_content.enabled',
            'order': 'updated',
            'limit': 20
        }

        self.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cookie': '_xsrf=QtQYs1eJS09ljvrPfqFCXAW0OOaLWHdc; _zap=672ebaef-912f-4b40-b624-faf6b8d8b14e; d_c0=AHDTO_fz5hePTtHbMXfCMVDK_F7CFpEMmWk=|1703415984; __snaker__id=3nqsd1yw3wiDuujA; q_c1=a760c1da4726457eb930fac54a6efa24|1705068771000|1705068771000; tst=h; z_c0=2|1:0|10:1725181703|4:z_c0|80:MS4xaHZTYUF3QUFBQUFtQUFBQVlBSlZUUWQ5d1djRFRmUnhqYnRWaVFSbjdIMkhlVzhtZFM3cUl3PT0=|08975083f7c5dbf93a81022e45664bdd6c77242da8c88e2f1ebe674c273e5770; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1725181704,1727506674; HMACCOUNT=2D4CF18D6B9898D5; SESSIONID=UUsvneEw8UQw9YbfRPKNLAro6jG7A4dprXEeGxs2Giu; JOID=VVgQCkP_oR_lzpPeRfHJSiwpyDhQrfFgkq_xnj7I80ue9sW7Jg8A5Y3GkddIUW3rW3CggaKRsFBPRrbff4xeZek=; osd=V1odCkv9oxLlxpHcSPHBSC4kyDBSr_xgmq3zkz7A8UmT9s25JAIA7Y_EnNdAU2_mW3iig6-RuFJPRrbff4xeZek=; __zse_ck=003_b7Gm0L6TklZT5xhKcdTlcXWvba+uZsLSJ62BOr4IaG15rXwH89GmtcNzqzMXXkTrpFYcUPE8t1MSpXxXzkvT3IgBbDihL8UuPsMASL2aJu8F; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1727506922; BEC=d892da65acb7e34c89a3073e8fa2254f',
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
        })

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