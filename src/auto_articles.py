import os
import logging
import os
from openai import OpenAI # type: ignore
from weibo_crawler import WeiboCrawler
import prompts


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_openai_client():
    client = OpenAI(api_key=os.getenv('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com")
    return client

def generate_article_titles(weibo_id, analysis_file, client):
    """
    Generate 10 article titles based on the Weibo post and its comments.
    """
    crawler = WeiboCrawler()

    # Fetch Weibo detail and comments
    detail = crawler.crawl_weibo_detail(weibo_id)
    comments = crawler.crawl_weibo_comments(weibo_id)

    # Log the fetched Weibo detail and comments list
    logging.info("Fetched Weibo detail: %s", detail)
    logging.info("Fetched Weibo comments list: %s", comments)

    if not detail or not comments:
        logging.error("Failed to fetch Weibo detail or comments for id: %s", weibo_id)
        return []

    # Read analysis content
    with open(analysis_file, 'r', encoding='utf-8') as file:
        analysis_content = file.read()
    logging.info("Analysis content: %s", analysis_content)

    # Generate article titles
    messages = [
        {
            "role": "system",
            "content": prompts.TOUTIAO_ROLE_PROMPT
        },
        {
            "role": "user", 
            "content": prompts.TOUTIAO_ARTICLE_TITLE_PROMPT.format(detail=detail, comments=comments, analysis_content=analysis_content)
        }
    ]
    logging.info("Message content: %s", messages)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    titles = [choice.message.content for choice in response.choices]
    return titles
    


if __name__ == "__main__":
    logging.info("Starting auto article generation")
    weibo_id = '5076707294580158'
    anlysis_file = './model/analysis_result_20240912_145206.md'
    titles = generate_article_titles(weibo_id, anlysis_file, init_openai_client())
    for title in titles:
        logging.info("Generated title: %s", title)