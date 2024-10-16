import requests
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 常量定义
ACCESS_TOKEN_EXPIRES = 300
FAKE_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Origin': 'https://kimi.moonshot.cn',
    'R-Timezone': 'Asia/Shanghai',
    'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
access_token_map = {}

def request_token(refresh_token):
    url = 'https://kimi.moonshot.cn/api/auth/token/refresh'
    headers = {
        'Authorization': f'Bearer {refresh_token}',
        'Accept': '*/*'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        return access_token, refresh_token
    else:
        logger.error(f"Failed to refresh token: {response.text}")
        return None, None

def acquire_token(refresh_token):
    if refresh_token in access_token_map:
        token_info = access_token_map[refresh_token]
        if time.time() < token_info['expires_at']:
            return token_info['access_token']
    
    access_token, refresh_token = request_token(refresh_token)
    if access_token:
        access_token_map[refresh_token] = {
            'access_token': access_token,
            'expires_at': time.time() + ACCESS_TOKEN_EXPIRES
        }
        return access_token
    return None

def pre_sign_url(filename, refresh_token):
    access_token = acquire_token(refresh_token)
    if not access_token:
        return None
    
    url = 'https://kimi.moonshot.cn/api/pre-sign-url'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*',
        **FAKE_HEADERS
    }
    payload = {
        'action': 'file',
        'name': filename
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get('url'), data.get('object_name')
    else:
        logger.error(f"Failed to get pre-sign URL: {response.text}")
        return None, None

def upload_file(file_path, refresh_token):
    filename = file_path.split('/')[-1]
    upload_url, object_name = pre_sign_url(filename, refresh_token)
    if not upload_url:
        return None
    
    with open(file_path, 'rb') as file_data:
        response = requests.put(upload_url, headers={'Content-Type': 'application/octet-stream'}, data=file_data)
        if response.status_code == 200:
            return object_name
        else:
            logger.error(f"Failed to upload file: {response.text}")
            return None

def summarize_file(file_path, refresh_token):
    object_name = upload_file(file_path, refresh_token)
    if not object_name:
        return None
    
    access_token = acquire_token(refresh_token)
    if not access_token:
        return None
    
    url = 'https://kimi.moonshot.cn/api/prompt-snippet/instance'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*',
        **FAKE_HEADERS
    }
    payload = {
        "offset": 0,
        "size": 10,
        "query": f"Summarize the content of the file: {object_name}"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        logger.error(f"Failed to summarize file: {response.text}")
        return None

# 示例用法
if __name__ == "__main__":
    refresh_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcyOTA3OTA2MiwiaWF0IjoxNzI5MDc4MTYyLCJqdGkiOiJjczdxNzRpbjZ2dWttZ3B1c2I0MCIsInR5cCI6ImFjY2VzcyIsImFwcF9pZCI6ImtpbWkiLCJzdWIiOiJjbnZwNnBzdWR1NmY4ODExOTRjZyIsInNwYWNlX2lkIjoiY252cDZwc3VkdTZmODgxMTk0YzAiLCJhYnN0cmFjdF91c2VyX2lkIjoiY252cDZwc3VkdTZmODgxMTk0YmcifQ.sjPlJJhl0i-UirYx-5IFYrPXbnnB3XWjvz3MrUvIMj7HTbnUe_4PN3DFKEaLqNmlKRFzWOX80hMkMzjo2nlRGg"

    file_path = "file:///Users/gqlin/Documents/workspace/auto-coder-demo/auto-zmt/7405504703687115273.docx"
    summary = summarize_file(file_path, refresh_token)
    if summary:
        print("File Summary:", summary)
    else:
        print("Failed to summarize the file.")