import datetime
import json
import csv
import os
import random
import time
import logging

import requests
from native_filter import DFAFilter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pypandoc


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Add a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

filter_sources = ['央视网', '新华社', '央视新闻']

class toutiaoCrawler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def process_response(self, response, timestamp):
        self.logger.info(f"Starting to process response with timestamp: {timestamp}")
        data = response
        if not data.get('data'):
            self.logger.warning("No data found in response")
            return    

        if not os.path.exists('articles/titles'):
            self.logger.info("Creating articles/titles directory")
            os.makedirs('articles/titles')
        csv_file_path = os.path.join('articles', 'titles', f'extracted_data_{timestamp}.csv')
        top_articles_path = os.path.join('articles', 'top_articles.csv')
        file_exists = os.path.isfile(csv_file_path)    
        
        self.logger.info(f"Processing data to CSV file: {csv_file_path}")
        titles_written = {}    

        try:
            with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
                fieldnames = ['title', 'publish_time', 'like_count', 'comment_count', 'media_name', 'source', 'abstract', 'article_url', 'tag', 'is_yaowen', 'article_sub_type', 'has_video']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)    

                if not file_exists:
                    self.logger.info("Creating new CSV file with headers")
                    writer.writeheader()    

                self.logger.info(f"Processing {len(data['data'])} articles")
                for item in data['data']:
                    title = item.get('title', '')
                    publish_time = datetime.datetime.fromtimestamp(int(item.get('publish_time', 0))).strftime('%Y-%m-%d %H:%M')    

                    if item.get('like_count', 0) > 100 and item.get('comment_count', 0) > 100:
                        if title not in titles_written:
                            self.logger.debug(f"Processing article: {title[:30]}... (likes: {item.get('like_count')}, comments: {item.get('comment_count')})")
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
                                'article_sub_type': item.get('article_sub_type', ''),
                                'has_video': item.get('has_video', '')
                            }    

                for title, row in titles_written.items():
                    writer.writerow(row)
                self.logger.info(f"Successfully wrote {len(titles_written)} articles to {csv_file_path}")
        except Exception as e:
            self.logger.error(f"Error processing response: {str(e)}", exc_info=True)
            raise

        self.logger.info("Starting to merge with top articles")
        # Merge with top_articles.csv and sort by like_count
        top_articles = []
        if os.path.exists(top_articles_path):
            self.logger.info(f"Reading existing top articles from {top_articles_path}")
            with open(top_articles_path, mode='r', encoding='utf-8') as top_file:
                reader = csv.DictReader(top_file)
                top_articles = list(reader)
                self.logger.info(f"Found {len(top_articles)} existing top articles")   

        unique_titles = set()
        deduplicated_articles = []    

        self.logger.info("Deduplicating articles")
        for title, row in titles_written.items():
            if title not in unique_titles:
                unique_titles.add(title)
                deduplicated_articles.append(row)    

        for article in top_articles:
            if article['title'] not in unique_titles:
                unique_titles.add(article['title'])
                deduplicated_articles.append(article)    

        # Initialize DFA filter
        self.logger.info("Initializing DFA filter")
        dfa_filter = DFAFilter()
        keywords_path = os.path.join(os.path.dirname(__file__), 'keywords')
        dfa_filter.parse(keywords_path)

        # Filter out articles with sensitive words
        original_count = len(deduplicated_articles)
        filtered_articles = []
        
        self.logger.info("Starting sensitive word filtering")
        for article in deduplicated_articles:
            title = str(article.get('title', ''))
            if not title:
                continue
                
            filtered_title = dfa_filter.filter(title)
            if filtered_title != title:  # 如果过滤后的标题与原标题不同，说明包含敏感词
                self.logger.info(f"Filtered title with sensitive words: {title} -> {filtered_title}")
            else:
                filtered_articles.append(article)
        
        filtered_count = original_count - len(filtered_articles)
        self.logger.info(f"Filtered out {filtered_count} articles with sensitive words")
        
        deduplicated_articles = filtered_articles

        # Filter out articles with has_video=1
        video_count = len([a for a in deduplicated_articles if a.get('has_video', '') == 1])
        deduplicated_articles = [article for article in deduplicated_articles if article.get('has_video', '') != 1]
        self.logger.info(f"Filtered out {video_count} articles with videos")
        
        deduplicated_articles = sorted(deduplicated_articles, key=lambda x: int(x['like_count']), reverse=True)[:500]    
        self.logger.info(f"Selected top 500 articles based on like count")

        # Remove the 'has_video' field from each article
        for article in deduplicated_articles:
            article.pop('has_video', None)    

        self.logger.info(f"Writing final results to {top_articles_path}")
        with open(top_articles_path, mode='w', newline='', encoding='utf-8') as top_file:
            fieldnames = ['title', 'publish_time', 'like_count', 'comment_count', 'media_name', 'source', 'abstract', 'article_url', 'tag', 'is_yaowen', 'article_sub_type']
            writer = csv.DictWriter(top_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in deduplicated_articles:
                writer.writerow(row)
            self.logger.info(f"Successfully wrote {len(deduplicated_articles)} articles to {top_articles_path}")

    def articles_request(self):
        self.logger.info("Starting articles request")
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
        max_pages = int(os.getenv('CRAWLER_MAX_PAGES', '5'))  # Set default to 5 pages
        self.logger.info(f"Will crawl maximum of {max_pages} pages")
        next_max_behot_time = None
        timestamp = int(time.time())    

        request_count = 0
        processed_titles = set()
        all_data = []    

        while page < max_pages:
            if next_max_behot_time is not None:
                max_behot_time_readable = datetime.datetime.fromtimestamp(next_max_behot_time).strftime('%Y-%m-%d %H:%M:%S')
                self.logger.info(f"Processing page {page + 1} of {max_pages}, max_behot_time: {max_behot_time_readable}")
            else:
                self.logger.info(f"Processing page {page + 1} of {max_pages}, max_behot_time: None")
            if page > 0:
                params['max_behot_time'] = next_max_behot_time
            try:
                self.logger.info(f"Making request to {base_url}")
                response = requests.get(base_url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                self.logger.info(f"Successfully received response for page {page + 1}")
            except requests.RequestException as e:
                self.logger.error(f"Request failed: {str(e)}", exc_info=True)
                break    

            if not data.get('data'):
                self.logger.warning("No data found in response, stopping pagination")
                break    

            self.logger.info(f"Filtering out articles from sources: {filter_sources}")
            filtered_data = [item for item in data['data'] if item.get('source', '') not in filter_sources]
            self.logger.info(f"Found {len(filtered_data)} articles after filtering (from {len(data['data'])} total)")
            all_data.extend(filtered_data)    

            behot_times = [item.get('behot_time', float('inf')) for item in data.get('data', [])]
            next_max_behot_time = min(behot_times) if behot_times else None
            if not next_max_behot_time:
                self.logger.warning("No more behot_time found, stopping pagination")
                break    

            page += 1
            request_count += 1
            self.logger.info(f"Sleeping for 5 seconds before next request")
            time.sleep(5)

        self.logger.info(f"Finished crawling {request_count} pages, processing response")
        # Remove duplicates
        unique_data = []
        processed_titles = set()
        for item in all_data:
            title = item.get('title', '')
            if title not in processed_titles:
                processed_titles.add(title)
                unique_data.append(item)
        
        if unique_data:  # Only process if we have data
            self.logger.info(f"Processing {len(unique_data)} unique articles")
            response_data = {'data': unique_data}
            self.process_response(response_data, timestamp)
        else:
            self.logger.warning("No articles found to process")

    def download_titles(self, max_downloads=10):
        top_articles_path = os.path.join('articles', 'top_articles.csv')
        if not os.path.exists(top_articles_path):
            logger.error(f"File {top_articles_path} does not exist.")
            return    

        driver_path = "./chromedriver-mac-arm64/chromedriver"
        service = Service(driver_path)
        browser = webdriver.Chrome(service=service)

        try:
            with open(top_articles_path, mode='r', encoding='utf-8') as top_file:
                reader = csv.DictReader(top_file)
                download_count = 0
                for row in reader:
                    if download_count >= max_downloads:
                        break
                    article_url = row.get('article_url', '')
                    title = row.get('title', '').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                    if not article_url or not title:
                        logger.warning(f"Skipping article with missing URL or title: {row}")
                        continue    

                    # Check if the URL is from toutiao.com
                    if not article_url.startswith('https://toutiao.com'):
                        logger.warning(f"Skipping article with non-toutiao.com URL: {article_url}")
                        continue    

                    try:
                        logger.info(f"Downloaded article: {title}, url: {article_url}")

                        if not os.path.exists('articles/details'):
                            os.makedirs('articles/details')
                        html_output_path = os.path.join('articles/details', f'{title}.html')
                        docx_output_path = os.path.join('articles/details', f'{title}.docx')

                        if not os.path.exists(html_output_path) and not os.path.exists(docx_output_path):
                            with open(html_output_path, 'w', encoding='utf-8') as file:
                                browser.get(article_url)
                                time.sleep(10)
                                textContainer = browser.find_element(By.CLASS_NAME, "syl-article-base")
                                articleHtml = textContainer.get_attribute("innerHTML")
                                file.write(articleHtml)
                                logger.info(f"Downloaded article: {title} success, url: {article_url}")

                            # Convert HTML to docx
                            pypandoc.convert_text(articleHtml, 'docx', format='html', outputfile=docx_output_path)
                            logger.info(f"Converted article to docx: {title}")
                            time.sleep(random.randint(1, 5))
                            download_count += 1
                        else:
                            logger.info(f"Article {title} already exists, skipping download.")
                    except Exception as e:
                        logger.error(f"Failed to download or convert article {title}: {e}")
        finally:
            browser.quit()

if __name__ == "__main__":
    toutiaoCrawler = toutiaoCrawler()
    toutiaoCrawler.articles_request()
    # toutiaoCrawler.download_titles(max_downloads=20)