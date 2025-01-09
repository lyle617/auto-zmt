"""Configuration settings for the crawler."""
import os

class Config:
    # Crawler settings
    MAX_TOP_ARTICLES = 500
    FILTER_SOURCES = ['央视网', '新华社', '央视新闻']
    MIN_LIKE_COUNT = 100
    MIN_COMMENT_COUNT = 100
    MAX_PAGES = int(os.getenv('CRAWLER_MAX_PAGES', '5'))

    # File paths
    ARTICLES_DIR = 'articles'
    TITLES_DIR = os.path.join(ARTICLES_DIR, 'titles')
    TOP_ARTICLES_FILE = os.path.join(ARTICLES_DIR, 'top_articles.csv')
    KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), 'keywords')

    # Toutiao API settings
    BASE_URL = 'https://m.toutiao.com/list/'
    DEFAULT_PARAMS = {
        'tag': '__all__',
        'ac': 'wap',
        'count': '20',
        'format': 'json_raw',
        'aid': '1698'
    }
    
    # Request headers
    HEADERS = {
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

    # CSV field names
    ARTICLE_FIELDS = [
        'title', 'publish_time', 'like_count', 'comment_count', 'media_name',
        'source', 'abstract', 'article_url', 'tag', 'is_yaowen', 'article_sub_type'
    ]
    ARTICLE_FIELDS_WITH_VIDEO = ARTICLE_FIELDS + ['has_video']
