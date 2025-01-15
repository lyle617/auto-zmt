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
        timestamp_file = os.path.join(model_dir, f'analysis_result_{timestamp}.md')
        latest_file = os.path.join(model_dir, 'title_analysis_result.md')
        backup_file = os.path.join(model_dir, f'title_analysis_result_{timestamp}.bak')

        logging.info("Saving analysis result to %s", timestamp_file)
        
        # Convert JSON to markdown format
        analysis_data = analysis_result['choices'][0]['message']['content']
        # Remove ```json and ``` markers if present
        if analysis_data.startswith('```json') and analysis_data.endswith('```'):
            analysis_data = analysis_data[7:-3].strip()
        try:
            analysis_json = json.loads(analysis_data)
            
            markdown_content = f"# 标题分析报告\n\n"
            markdown_content += f"**生成时间:** {timestamp}\n\n"
            
            # 分析总结
            markdown_content += "## 分析总结\n"
            summary = analysis_json.get('analysis_summary', {})
            # markdown_content += f"### 量化分析\n{summary.get('quantitative_analysis', '')}\n\n" 
            markdown_content += f"### 方法论总结\n{summary.get('methodology_summary', '')}\n\n"
            
            # 关键词统计
            markdown_content += "## 关键词统计\n"
            keyword_stats = analysis_json.get('keyword_stats', {})
            
            # 高频关键词
            markdown_content += "### 高频关键词\n"
            markdown_content += "| 关键词 | 频率 | 情感倾向 |\n"
            markdown_content += "|--------|------|----------|\n"
            for kw in keyword_stats.get('high_frequency_keywords', []):
                keyword = kw.get('关键词', kw.get('keyword', ''))
                frequency = kw.get('频率', kw.get('frequency', ''))
                sentiment = kw.get('情感倾向', kw.get('sentiment', ''))
                markdown_content += f"| {keyword} | {frequency} | {sentiment} |\n"
            markdown_content += "\n"
            
            # 情感关键词
            markdown_content += "### 情感关键词\n"
            sentiment_kws = keyword_stats.get('emotional_keywords', keyword_stats.get('sentiment_keywords', {}))
            markdown_content += "- 正面: " + ", ".join(sentiment_kws.get('正面', [])) + "\n"
            markdown_content += "- 负面: " + ", ".join(sentiment_kws.get('负面', [])) + "\n"
            markdown_content += "- 中性: " + ", ".join(sentiment_kws.get('中性', [])) + "\n\n"
            
            # 关键词组合模式
            markdown_content += "### 关键词组合模式\n"
            combination_patterns = keyword_stats.get('keyword_combination_patterns', '')
            markdown_content += f"{combination_patterns}\n\n"
            
            # 结构统计
            markdown_content += "## 结构统计\n"
            structure_stats = analysis_json.get('structure_stats', {})
            
            markdown_content += "### 标题长度分布\n"
            length_dist = structure_stats.get('title_length_distribution', {})
            if isinstance(length_dist, dict):
                for length, count in length_dist.items():
                    markdown_content += f"- {length}: {count}%\n"
            else:
                markdown_content += f"- {length_dist}\n"
            markdown_content += "\n"
            
            markdown_content += "### 标点符号使用频率\n"
            punct_freq = structure_stats.get('punctuation_frequency', {})
            if isinstance(punct_freq, dict):
                for punct, count in punct_freq.items():
                    markdown_content += f"- {punct}: {count}次\n"
            else:
                markdown_content += f"- {punct_freq}\n"
            markdown_content += "\n"
            
            markdown_content += "### 句式结构\n"
            sentence_struct = structure_stats.get('sentence_structure', {})
            if isinstance(sentence_struct, dict):
                for struct, count in sentence_struct.items():
                    markdown_content += f"- {struct}: {count}%\n"
            else:
                markdown_content += f"- {sentence_struct}\n"
            markdown_content += "\n"
            
            # 效果分析
            markdown_content += "## 效果分析\n"
            effect_analysis = analysis_json.get('effect_analysis', {})
            markdown_content += f"- 点击率相关性: {effect_analysis.get('click_through_rate_correlation', '')}\n"
            markdown_content += f"- 阅读完成率: {effect_analysis.get('completion_rate_by_length', '')}\n"
            markdown_content += f"- 情感与互动关系: {effect_analysis.get('emotional_impact_on_engagement', '')}\n\n"
            
            # 趋势分析
            markdown_content += "## 趋势分析\n"
            trend_analysis = analysis_json.get('trend_analysis', {})
            markdown_content += "### 近期热门标题特征\n"
            markdown_content += f"{trend_analysis.get('recent_trends', '')}\n\n"
            
            markdown_content += "### 季节性热点关键词\n"
            seasonal_keywords = trend_analysis.get('seasonal_keywords', {})
            for season, keywords in seasonal_keywords.items():
                markdown_content += f"- {season}: {', '.join(keywords)}\n"
            markdown_content += "\n"
            
            # 最佳实践
            markdown_content += "## 最佳实践\n"
            best_practices = analysis_json.get('best_practices', {})
            markdown_content += f"- 标题长度建议: {best_practices.get('title_length_recommendation', '')}\n"
            markdown_content += f"- 推荐句式结构: {best_practices.get('recommended_sentence_structure', '')}\n"
            markdown_content += f"- 情感关键词使用: {best_practices.get('emotional_keyword_usage', '')}\n"
            markdown_content += f"- 标点符号使用指南: {best_practices.get('punctuation_guidelines', '')}\n\n"
            
            # 示例标题
            markdown_content += "## 示例标题\n"
            example_titles = analysis_json.get('example_titles', [])
            for i, example in enumerate(example_titles, 1):
                title = example.get('标题', '')
                features = example.get('特征组合', '')
                markdown_content += f"{i}. **{title}**\n"
                markdown_content += f"    - 特征: {features}\n"
            markdown_content += "\n"
            
            # Save JSON format with detailed logging
            json_timestamp_file = timestamp_file.replace('.md', '.json')
            json_latest_file = latest_file.replace('.md', '.json')
            json_backup_file = backup_file.replace('.md', '.json')
            
            # Log JSON file paths
            logging.info(f"JSON timestamp file: {json_timestamp_file}")
            logging.info(f"JSON latest file: {json_latest_file}")
            logging.info(f"JSON backup file: {json_backup_file}")
            
            # Save JSON to timestamp file with size logging
            with open(json_timestamp_file, 'w', encoding='utf-8') as json_file:
                json.dump(analysis_json, json_file, ensure_ascii=False, indent=2)
                json_file_size = os.path.getsize(json_timestamp_file)
                logging.info(f"Saved JSON to timestamp file. Size: {json_file_size} bytes")
            
            # Backup existing title_analysis_result.json if it exists
            if os.path.exists(json_latest_file):
                original_size = os.path.getsize(json_latest_file)
                logging.info(f"Backing up existing title_analysis_result.json (size: {original_size} bytes) to {json_backup_file}")
                os.rename(json_latest_file, json_backup_file)
                backup_size = os.path.getsize(json_backup_file)
                logging.info(f"Backup complete. Backup file size: {backup_size} bytes")
            
            # Save JSON to latest file with size logging
            with open(json_latest_file, 'w', encoding='utf-8') as json_file:
                json.dump(analysis_json, json_file, ensure_ascii=False, indent=2)
                latest_file_size = os.path.getsize(json_latest_file)
                logging.info(f"Saved JSON to latest file. Size: {latest_file_size} bytes")
                logging.info(f"JSON structure keys: {list(analysis_json.keys())}")
            
            # Save Markdown format
            with open(timestamp_file, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)
            
            # Backup existing title_analysis_result.md if it exists
            if os.path.exists(latest_file):
                logging.info(f"Backing up existing title_analysis_result.md to {backup_file}")
                os.rename(latest_file, backup_file)
            
            # Save Markdown to latest file
            with open(latest_file, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)
        except json.JSONDecodeError:
            # If response is not JSON, save as plain text
            with open(timestamp_file, 'w', encoding='utf-8') as md_file:
                md_file.write(f"# Analysis Result\n\n{analysis_data}")
            # Also save as JSON with raw text
            json_timestamp_file = timestamp_file.replace('.md', '.json')
            with open(json_timestamp_file, 'w', encoding='utf-8') as json_file:
                json.dump({"raw_text": analysis_data}, json_file, ensure_ascii=False, indent=2)
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