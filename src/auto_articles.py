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

    # TODO: Implement the logic to generate 10 article titles based on the model's analysis
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