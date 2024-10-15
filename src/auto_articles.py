import os
import logging
import argparse
from openai import OpenAI # type: ignore
from weibo_crawler import WeiboCrawler
import prompts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_openai_client():
    client = OpenAI(api_key=os.getenv('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com")
    return client

def generate_article_titles_and_log(weibo_id, analysis_file, detail, comments, client):
    """
    Generate 10 article titles based on the Weibo post and its comments, and log the results.
    """
    titles = generate_article_titles(weibo_id, analysis_file, detail, comments, client)
    for title in titles:
        logging.info("Generated title: \n%s", title)
        logging.info("=====================================")
        logging.info("Detail content: \n%s", detail)
    return titles
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate article titles based on Weibo post and its comments.")
    parser.add_argument('weibo_id', type=str, help='Weibo ID to fetch details and comments')
    parser.add_argument('question_id', type=str, help='Question ID for analysis')
    args = parser.parse_args()

    logging.info("Starting auto article generation")
    weibo_id = args.weibo_id
    anlysis_file = f'./analysis_result/title_analysis_result.md'

    # Fetch Weibo detail and comments
    crawler = WeiboCrawler()
    detail = crawler.crawl_weibo_detail(weibo_id)
    comments = crawler.crawl_weibo_comments(weibo_id)

    titles = generate_article_titles_and_log(weibo_id, anlysis_file, detail, comments, init_openai_client())