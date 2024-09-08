import logging
import requests
import json
import csv
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def deepseek_api_call(titles):
    logging.info("Starting deepseek_api_call function")
    api_url = "https://api.deepseek.com/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('DEEPSEEK_TOKEN')
    }
    payload = json.dumps({
      "messages": [
        {
          "content": "你是一个资深的今日头条文章创作者",
          "role": "system"
        },
        {
          "content": '请分析以下高点击数、高评论数的文章的标题，总结文章标题的撰写范式：' + ' '.join(titles),
          "role": "user"
        }
      ],
      "model": "deepseek-coder",
      "frequency_penalty": 0,
      "max_tokens": 2048,
      "presence_penalty": 0,
      "response_format": {
        "type": "text"
      },
      "stop": None,
      "stream": False,
      "stream_options": None,
      "temperature": 1,
      "top_p": 1,
      "tools": None,
      "tool_choice": "none",
      "logprobs": False,
      "top_logprobs": None
    })

    logging.info("Sending API request to %s", api_url)
    response = requests.request("POST", api_url, headers=headers, data=payload)
    if response.status_code == 200:
        logging.info("API call successful")
        analysis_result = response.json()
        logging.info("API response: %s", analysis_result['choices'][0]['message']['content'])

        # Create the ./model directory if it doesn't exist
        model_dir = './model'
        if not os.path.exists(model_dir):
            logging.info("Creating directory: %s", model_dir)
            os.makedirs(model_dir)

        # Save the analysis result to a markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        markdown_file_path = os.path.join(model_dir, f'analysis_result_{timestamp}.md')
        logging.info("Saving analysis result to %s", markdown_file_path)
        with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# Analysis Result\n\n{analysis_result['choices'][0]['message']['content']}")
    else:
        logging.error("API call failed with status code: %s", response.status_code)

def read_titles_from_csv(file_path):
    logging.info("Reading titles from CSV file: %s", file_path)
    titles = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            titles.append(row['title'])
    logging.info("Found %d titles", len(titles))
    return titles

if __name__ == "__main__":
    logging.info("Starting main execution")
    csv_file_path = os.path.join('articles', 'top_articles.csv')
    titles = read_titles_from_csv(csv_file_path)
    deepseek_api_call(titles)