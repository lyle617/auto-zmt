import requests
import json
import csv
import os

def deepseek_api_call(titles):
    api_url = "https://api.deepseek.com/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer {token}'
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

    response = requests.request("POST", api_url, headers=headers, data=payload)
    if response.status_code == 200:
        print("API call successful")
        print(response.json())
    else:
        print("API call failed with status code:", response.status_code)

def read_titles_from_csv(file_path):
    titles = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            titles.append(row['title'])
    return titles

if __name__ == "__main__":
    csv_file_path = os.path.join('articles', 'top_articles.csv')
    titles = read_titles_from_csv(csv_file_path)
    deepseek_api_call(titles)