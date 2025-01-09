import logging
import requests
import json
import csv
import os
from datetime import datetime
import prompts
from native_filter import DFAFilter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_titles_with_deepseek(titles):
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
          "content": prompts.TOUTIAO_ROLE_PROMPT,
          "role": "system"
        },
        {
          "content": f'{prompts.TOUTIAO_TITLE_ANALYSIS_PROMPT} {titles}',
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
        
        # Convert JSON to markdown format
        analysis_data = analysis_result['choices'][0]['message']['content']
        try:
            analysis_json = json.loads(analysis_data)
            
            markdown_content = f"# Title Analysis Report\n\n"
            markdown_content += f"**Generated at:** {timestamp}\n\n"
            
            # Add analysis summary
            markdown_content += "## Analysis Summary\n"
            markdown_content += analysis_json.get('analysis_summary', '') + "\n\n"
            
            # Add keyword statistics
            markdown_content += "## Keyword Statistics\n"
            markdown_content += "| Keyword | Frequency | Sentiment |\n"
            markdown_content += "|---------|-----------|-----------|\n"
            for kw in analysis_json.get('keyword_stats', []):
                markdown_content += f"| {kw.get('keyword', '')} | {kw.get('frequency', '')} | {kw.get('sentiment', '')} |\n"
            markdown_content += "\n"
            
            # Add structure statistics
            markdown_content += "## Structure Statistics\n"
            markdown_content += "| Metric | Value |\n"
            markdown_content += "|--------|-------|\n"
            for stat in analysis_json.get('structure_stats', []):
                markdown_content += f"| {stat.get('metric', '')} | {stat.get('value', '')} |\n"
            markdown_content += "\n"
            
            # Add best practices
            markdown_content += "## Best Practices\n"
            for practice in analysis_json.get('best_practices', []):
                markdown_content += f"- {practice}\n"
            markdown_content += "\n"
            
            # Add example titles
            markdown_content += "## Example Titles\n"
            for i, title in enumerate(analysis_json.get('example_titles', []), 1):
                markdown_content += f"{i}. {title}\n"
            
            with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)
        except json.JSONDecodeError:
            # If response is not JSON, save as plain text
            with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(f"# Analysis Result\n\n{analysis_data}")
    else:
        logging.error("API call failed with status code: %s", response.status_code)

def read_titles_from_csv(file_path):
    logging.info("Reading titles from CSV file: %s", file_path)
    titles = []
    dfa_filter = DFAFilter()
    # Use absolute path for keywords file
    keywords_path = os.path.join(os.path.dirname(__file__), 'keywords')
    dfa_filter.parse(keywords_path)
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['title']
            filtered_title = dfa_filter.filter(title, repl="*")
            logging.info("Original title: %s, Filtered title: %s", title, filtered_title)
            titles.append((int(row['like_count']), filtered_title))
    
    # Sort titles by like_count in descending order
    titles.sort(reverse=True, key=lambda x: x[0])
    
    # Select the top 150 titles
    top_titles = [title for _, title in titles[:150]]
    
    logging.info("Found %d titles with the highest like_count", len(top_titles))
    return top_titles

if __name__ == "__main__":
    logging.info("Starting main execution")
    csv_file_path = os.path.join('articles', 'top_articles.csv')
    titles = read_titles_from_csv(csv_file_path)
    analyze_titles_with_deepseek(titles)