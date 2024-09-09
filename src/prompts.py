import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOUTIAO_ROLE_PROMPT = "你是一个资深的今日头条爆款文章创作者，擅长撰写关于每日热点新闻的爆款文章。"
TOUTIAO_TITLE_ANALYSIS_PROMPT = "分析以下高点击数、高评论数的爆款文章标题的规及特点，然后总结归纳爆款文章的标题范式，同时提炼关键词"
