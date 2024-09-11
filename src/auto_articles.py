import os
import logging
from weibo_crawler import fetch_weibo_detail, fetch_weibo_comments, save_comments_to_csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_article_titles(weibo_id):
    """
    Generate 10 article titles based on the Weibo post and its comments.
    """
    # Fetch Weibo detail and comments
    detail = fetch_weibo_detail(weibo_id)
    comments = fetch_weibo_comments(weibo_id)

    if not detail or not comments:
        logging.error("Failed to fetch Weibo detail or comments for id: %s", weibo_id)
        return []

    # Save comments to CSV
    save_comments_to_csv(comments['data']['data'], os.path.join('weibo_results', f'weibo_comments_{weibo_id}.csv'))

    import os
from openai import OpenAI

client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

def generate_article_titles(analysis_file):
    with open(analysis_file, 'r', encoding='utf-8') as file:
        analysis_content = file.read()

    messages = [{"role": "user", "content": f"Generate 10 article titles based on the following analysis:\n{analysis_content}"}]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    titles = [choice.message.content for choice in response.choices]
    return titles

# Example usage
analysis_file = "model/analysis_result_20240910_001316.md"
titles = generate_article_titles(analysis_file)
for i, title in enumerate(titles, 1):
    print(f"Title {i}: {title}")
    # For now, we will just return some placeholder titles
    titles = [
        f"Title 1 for Weibo ID {weibo_id}",
        f"Title 2 for Weibo ID {weibo_id}",
        f"Title 3 for Weibo ID {weibo_id}",
        f"Title 4 for Weibo ID {weibo_id}",
        f"Title 5 for Weibo ID {weibo_id}",
        f"Title 6 for Weibo ID {weibo_id}",
        f"Title 7 for Weibo ID {weibo_id}",
        f"Title 8 for Weibo ID {weibo_id}",
        f"Title 9 for Weibo ID {weibo_id}",
        f"Title 10 for Weibo ID {weibo_id}"
    ]

    return titles

if __name__ == "__main__":
    logging.info("Starting auto article generation")
    weibo_id = '5076707294580158'
    titles = generate_article_titles(weibo_id)
    for title in titles:
        logging.info("Generated title: %s", title)