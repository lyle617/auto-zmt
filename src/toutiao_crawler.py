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
import pypandoc
from config import Config


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

class ToutiaoCrawler:
    def __init__(self):
        self.logger = logger
        self.config = Config()

    def _write_to_csv(self, data, csv_file_path, timestamp):
        """Write article data to CSV file."""
        file_exists = os.path.isfile(csv_file_path)
        titles_written = {}

        try:
            with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.config.ARTICLE_FIELDS_WITH_VIDEO)

                if not file_exists:
                    self.logger.info("Creating new CSV file with headers")
                    writer.writeheader()

                self.logger.info(f"Processing {len(data['data'])} articles")
                for item in data['data']:
                    title = item.get('title', '')
                    publish_time = datetime.datetime.fromtimestamp(int(item.get('publish_time', 0))).strftime('%Y-%m-%d %H:%M')

                    if (item.get('like_count', 0) > self.config.MIN_LIKE_COUNT and 
                        item.get('comment_count', 0) > self.config.MIN_COMMENT_COUNT and
                        item.get('source', '') not in self.config.FILTER_SOURCES):
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
                                'article_sub_type': item.get('article_sub_type', ''),
                                'has_video': item.get('has_video', '')
                            }

                for title, row in titles_written.items():
                    writer.writerow(row)
                self.logger.info(f"Successfully wrote {len(titles_written)} articles to {csv_file_path}")
                return titles_written
        except Exception as e:
            self.logger.error(f"Error writing to CSV: {str(e)}", exc_info=True)
            raise

    def _filter_articles(self, articles):
        """Filter articles based on sensitive words and video content."""
        # Initialize DFA filter
        self.logger.info("Initializing DFA filter")
        dfa_filter = DFAFilter()
        dfa_filter.parse(self.config.KEYWORDS_PATH)

        # Filter out articles with sensitive words
        original_count = len(articles)
        filtered_articles = []
        
        self.logger.info("Starting sensitive word filtering")
        for article in articles:
            title = str(article.get('title', ''))
            if not title:
                continue
                
            filtered_title = dfa_filter.filter(title)
            if filtered_title != title:
                self.logger.info(f"Filtered title with sensitive words: {title} -> {filtered_title}")
            else:
                filtered_articles.append(article)
        
        filtered_count = original_count - len(filtered_articles)
        self.logger.info(f"Filtered out {filtered_count} articles with sensitive words")

        # Filter out articles with has_video=1
        video_count = len([a for a in filtered_articles if a.get('has_video', '') == 1])
        filtered_articles = [article for article in filtered_articles if article.get('has_video', '') != 1]
        self.logger.info(f"Filtered out {video_count} articles with videos")

        return filtered_articles

    def _merge_top_articles(self, new_articles, top_articles_path):
        """Merge new articles with existing top articles and sort by like count."""
        top_articles = []
        if os.path.exists(top_articles_path):
            self.logger.info(f"Reading existing top articles from {top_articles_path}")
            with open(top_articles_path, mode='r', encoding='utf-8') as top_file:
                reader = csv.DictReader(top_file)
                top_articles = list(reader)
                self.logger.info(f"Found {len(top_articles)} existing top articles")

        # Combine and deduplicate articles
        unique_titles = set()
        deduplicated_articles = []

        for title, article in new_articles.items():
            if title not in unique_titles:
                unique_titles.add(title)
                deduplicated_articles.append(article)

        for article in top_articles:
            if article['title'] not in unique_titles:
                unique_titles.add(article['title'])
                deduplicated_articles.append(article)

        # Filter and sort articles
        filtered_articles = self._filter_articles(deduplicated_articles)
        
        # Filter out articles from sources in FILTER_SOURCES
        source_filtered_articles = [
            article for article in filtered_articles 
            if article.get('source', '') not in self.config.FILTER_SOURCES
        ]
        
        # Sort by like_count and take top articles
        sorted_articles = sorted(source_filtered_articles, key=lambda x: int(x['like_count']), reverse=True)[:self.config.MAX_TOP_ARTICLES]
        
        # Log filtering results
        self.logger.info(f"Filtered out {len(filtered_articles) - len(source_filtered_articles)} articles from sources: {self.config.FILTER_SOURCES}")

        # Remove the 'has_video' field from each article
        for article in sorted_articles:
            article.pop('has_video', None)

        return sorted_articles

    def process_response(self, response, timestamp):
        """Process the response data and save to CSV files."""
        self.logger.info(f"Starting to process response with timestamp: {timestamp}")
        data = response
        if not data.get('data'):
            self.logger.warning("No data found in response")
            return

        if not os.path.exists(self.config.TITLES_DIR):
            self.logger.info(f"Creating directory: {self.config.TITLES_DIR}")
            os.makedirs(self.config.TITLES_DIR)

        csv_file_path = os.path.join(self.config.TITLES_DIR, f'extracted_data_{timestamp}.csv')

        # Write new articles to CSV
        titles_written = self._write_to_csv(data, csv_file_path, timestamp)

        # Merge with top articles and write results
        merged_articles = self._merge_top_articles(titles_written, self.config.TOP_ARTICLES_FILE)

        # Write final results to top_articles.csv
        self.logger.info(f"Writing final results to {self.config.TOP_ARTICLES_FILE}")
        with open(self.config.TOP_ARTICLES_FILE, mode='w', newline='', encoding='utf-8') as top_file:
            writer = csv.DictWriter(top_file, fieldnames=self.config.ARTICLE_FIELDS)
            writer.writeheader()
            for row in merged_articles:
                writer.writerow(row)
            self.logger.info(f"Successfully wrote {len(merged_articles)} articles to {self.config.TOP_ARTICLES_FILE}")

    def articles_request(self):
        """Request articles from Toutiao API."""
        self.logger.info("Starting articles request")
        params = self.config.DEFAULT_PARAMS.copy()
        params.update({
            'max_time': '1725409291',
            '_signature': 'oxib-wAAxdpfXCDdxPIW2KMYm-',
            'i': '1725409291',
            'as': 'A116960D97ABEFA',
            'cp': '66D7EB3EAFCA6E1',
        })

        page = 0
        all_data = []
        next_max_behot_time = None

        while page < self.config.MAX_PAGES:
            if next_max_behot_time:
                params['max_behot_time'] = next_max_behot_time

            try:
                response = requests.get(
                    self.config.BASE_URL,
                    params=params,
                    headers=self.config.HEADERS,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                self.logger.error(f"Error fetching data: {str(e)}", exc_info=True)
                break

            if not data.get('data'):
                self.logger.warning("No data found in response, stopping pagination")
                break

            self.logger.info(f"Filtering out articles from sources: {self.config.FILTER_SOURCES}")
            filtered_data = [item for item in data['data'] if item.get('source', '') not in self.config.FILTER_SOURCES]
            self.logger.info(f"Found {len(filtered_data)} articles after filtering (from {len(data['data'])} total)")
            all_data.extend(filtered_data)

            next_max_behot_time = data.get('next', {}).get('max_behot_time')
            if not next_max_behot_time:
                self.logger.warning("No next page token found, stopping pagination")
                break

            page += 1
            self.logger.info(f"Moving to page {page + 1}")
            time.sleep(random.uniform(1, 3))  # Random delay between requests

        timestamp = int(time.time())
        self.process_response({'data': all_data}, timestamp)

    def download_titles(self, max_downloads=10):
        top_articles_path = self.config.TOP_ARTICLES_FILE
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

                        if not os.path.exists(self.config.DETAILS_DIR):
                            os.makedirs(self.config.DETAILS_DIR)
                        html_output_path = os.path.join(self.config.DETAILS_DIR, f'{title}.html')
                        docx_output_path = os.path.join(self.config.DETAILS_DIR, f'{title}.docx')

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
    toutiaoCrawler = ToutiaoCrawler()
    toutiaoCrawler.articles_request()
    # toutiaoCrawler.download_titles(max_downloads=20)