import os
import logging
import os
from openai import OpenAI # type: ignore
from weibo_crawler import WeiboCrawler, save_comments_to_csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_openai_client():
    client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")
    return client

def generate_article_titles(weibo_id, analysis_file, client):
    """
    Generate 10 article titles based on the Weibo post and its comments.
    """
    crawler = WeiboCrawler()

    # Fetch Weibo detail and comments
    detail = crawler.fetch_weibo_detail(weibo_id)
    comments = crawler.fetch_weibo_comments(weibo_id)

    if not detail or not comments:
        logging.error("Failed to fetch Weibo detail or comments for id: %s", weibo_id)
        return []

    # Save comments to CSV
    save_comments_to_csv(comments['data']['data'], os.path.join('weibo_results', f'weibo_comments_{weibo_id}.csv'))

    # Read analysis content
    with open(analysis_file, 'r', encoding='utf-8') as file:
        analysis_content = file.read()

    # Generate article titles
    messages = [{"role": "user", "content": f"热搜详情:{detail}\n 热搜评论: {comments}\n 标题生成规律和范式：{analysis_content} \n 为上述的热搜按照标题生成规律和范式，生成10个30字以内的文章标题"}]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    titles = [choice.message.content for choice in response.choices]
    return titles
    


if __name__ == "__main__":
    logging.info("Starting auto article generation")
    weibo_id = '5076707294580158'
    anlysis_file = 'weibo_results/weibo_analysis_5076707294580158.txt'
    titles = generate_article_titles(weibo_id, anlysis_file, init_openai_client())
    for title in titles:
        logging.info("Generated title: %s", title)