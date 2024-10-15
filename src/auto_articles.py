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

def generate_article_titles(weibo_id, analysis_file, detail, comments, client):
    """
    Generate 10 article titles based on the Weibo post and its comments.
    """
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
    


def process_weibo_post(weibo_id, analysis_file):
    """
    Fetch Weibo detail and comments, and generate article titles.
    """
    crawler = WeiboCrawler()
    detail = crawler.crawl_weibo_detail(weibo_id)
    comments = crawler.crawl_weibo_comments(weibo_id)

    titles = generate_article_titles(weibo_id, analysis_file, detail, comments, init_openai_client())
    logging.info("Length of generated titles: %d", len(titles))
    if not titles:
        logging.error("No titles generated for Weibo ID: %s", weibo_id)
        return

    logging.info("Generated titles:")
    for i, title in enumerate(titles, 1):
        logging.info("%d. %s", i, title)

    while True:
        selected_index = int(input("Please select a title by entering its number (or enter 0 to regenerate titles): ")) - 1
        logging.info("Selected index: %d", selected_index)
        if selected_index == -1:
            logging.info("Regenerating titles...")
            titles = generate_article_titles(weibo_id, analysis_file, detail, comments, init_openai_client())
            logging.info("Length of regenerated titles: %d", len(titles))
            if not titles:
                logging.error("No titles generated for Weibo ID: %s", weibo_id)
                return
            logging.info("Generated titles:")
            for i, title in enumerate(titles, 1):
                logging.info("%d. %s", i, title)
        elif 0 <= selected_index < len(titles):
            selected_title = titles[selected_index]
            logging.info("Selected title: \n%s", selected_title)
            logging.info("=====================================")
            logging.info("Detail content: \n%s", detail)
            return selected_title, detail, comments
        else:
            logging.error("Invalid selection. Please try again.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate article titles based on Weibo post and its comments.")
    parser.add_argument('--weibo_id', type=str, help='Weibo ID to fetch details and comments')
    parser.add_argument('--question_id', type=str, help='Question ID for analysis')
    args = parser.parse_args()

    logging.info("Starting auto article generation")
    weibo_id = args.weibo_id
    analysis_file = f'./analysis_result/title_analysis_result.md'

    process_weibo_post(weibo_id, analysis_file)