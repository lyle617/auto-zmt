import os
import logging
import os
from openai import OpenAI # type: ignore
from weibo_crawler import WeiboCrawler
import prompts


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_openai_client():
    client = OpenAI(api_key="sk-c22ae6c9e1ef4e09b817758d2ce2dda1", base_url="https://api.deepseek.com")
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

    # Generate article titles
    messages = [
        {
            "role": "system",
            "content": prompts.TOUTIAO_ROLE_PROMPT
        },
        {
            "role": "user", 
            "content": f"热搜详情:{detail}\n 热搜评论列表: {comments}\n 基于上述的热搜详情结合评论列表按照以下爆款文章的标题分析 {analysis_content} ，生成10个30字以内的文章标题"
        }
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    titles = [choice.message.content for choice in response.choices]
    return titles
    


if __name__ == "__main__":
    logging.info("Starting auto article generation")
    weibo_id = '5076707294580158'
    anlysis_file = 'model/analysis_result_20240910_001316.md'
    titles = generate_article_titles(weibo_id, anlysis_file, init_openai_client())
    for title in titles:
        logging.info("Generated title: %s", title)