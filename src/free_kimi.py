import requests
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
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
    logger.info(f"Requesting token with refresh token: {refresh_token}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        logger.info(f"Token refresh successful. New access token: {access_token}, new refresh token: {refresh_token}")
        return access_token, refresh_token
    else:
        logger.error(f"Failed to refresh token: {response.text}")
        return None, None

def acquire_token(refresh_token):
    logger.info(f"Acquiring token for refresh token: {refresh_token}")
    if refresh_token in access_token_map:
        token_info = access_token_map[refresh_token]
        if time.time() < token_info['expires_at']:
            logger.info(f"Token found in cache. Access token: {token_info['access_token']}, expires at: {token_info['expires_at']}")
            return token_info['access_token']
    
    access_token, refresh_token = request_token(refresh_token)
    if access_token:
        access_token_map[refresh_token] = {
            'access_token': access_token,
            'expires_at': time.time() + ACCESS_TOKEN_EXPIRES
        }
        logger.info(f"Token acquired. Access token: {access_token}, expires at: {access_token_map[refresh_token]['expires_at']}")
        return access_token
    logger.warning("Failed to acquire token.")
    return None

def pre_sign_url(filename, refresh_token):
    access_token = acquire_token(refresh_token)
    if not access_token:
        logger.error("Failed to acquire access token for pre-sign URL request.")
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
    logger.info(f"Requesting pre-sign URL for file: {filename}")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            data = response.json()
            pre_sign_url = data.get('url')
            object_name = data.get('object_name')
            logger.info(f"Pre-sign URL request successful. URL: {pre_sign_url}, Object Name: {object_name}")
            return pre_sign_url, object_name
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Failed to decode JSON from response: {response.text}")
            return None, None
    else:
        logger.error(f"Failed to get pre-sign URL: {response.text}")
        return None, None

def upload_file(file_path, refresh_token):
    filename = file_path.split('/')[-1]
    logger.info(f"Uploading file: {filename}")
    upload_url, object_name = pre_sign_url(filename, refresh_token)
    if not upload_url:
        logger.error("Failed to get upload URL.")
        return None
    
    with open(file_path, 'rb') as file_data:
        response = requests.put(upload_url, headers={'Content-Type': 'application/octet-stream'}, data=file_data)
        if response.status_code == 200:
            logger.info(f"File upload successful. Object Name: {object_name}")
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
    
def create_conversation(model, name, refresh_token):
    access_token = acquire_token(refresh_token)
    if not access_token:
        return None
    
    url = 'https://kimi.moonshot.cn/api/chat'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*',
        **FAKE_HEADERS
    }
    payload = {
        'born_from': '',
        'is_example': False,
        'kimiplus_id': model,
        'name': name
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get('id')
    else:
        logger.error(f"Failed to create conversation: {response.text}")
        return None

def create_completion(model, messages, refresh_token, use_search=True, ref_conv_id=None, retry_count=0):
    if retry_count >= 3:
        logger.error("Max retry count reached")
        return None
    
    access_token = acquire_token(refresh_token)
    if not access_token:
        return None
    
    conv_id = ref_conv_id or create_conversation(model, "未命名会话", refresh_token)
    if not conv_id:
        return None
    
    url = f'https://kimi.moonshot.cn/api/chat/{conv_id}/completion/stream'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*',
        **FAKE_HEADERS
    }
    payload = {
        'kimiplus_id': model,
        'messages': messages,
        'use_search': use_search
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to create completion: {response.text}")
        return create_completion(model, messages, refresh_token, use_search, ref_conv_id, retry_count + 1)
    
# 示例用法
if __name__ == "__main__":
    refresh_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTczNjk5Njg2MywiaWF0IjoxNzI5MjIwODYzLCJqdGkiOiJjczh0MXZ1Y3A3ZmY0cTRpYmpsMCIsInR5cCI6InJlZnJlc2giLCJhcHBfaWQiOiJraW1pIiwic3ViIjoiY252cDZwc3VkdTZmODgxMTk0Y2ciLCJzcGFjZV9pZCI6ImNudnA2cHN1ZHU2Zjg4MTE5NGMwIiwiYWJzdHJhY3RfdXNlcl9pZCI6ImNudnA2cHN1ZHU2Zjg4MTE5NGJnIn0.mt34JkF7w20jHwlNrfQpSUgc8ZMWfymsrLDGlhGmQEWEJ7AVMFQmFzn9Mka0YlkkAAFQcaj-W3Sp61yBhvB3-Q"

    # file_path = "https://mj101-1317487292.cos.ap-shanghai.myqcloud.com/ai/test.pdf"
    # summary = summarize_file(file_path, refresh_token)
    # if summary:
    #     print("File Summary:", summary)
    # else:
    #     print("Failed to summarize the file.")
    model = "kimi"
    messages = [
        {"role": "user", "content": "你好，Kimi！"},
        {"role": "assistant", "content": "你好！有什么我可以帮助你的吗？"}
    ]
    
    completion = create_completion(model, messages, refresh_token)
    if completion:
        print("Completion:", completion)
    else:
        print("Failed to get completion.")