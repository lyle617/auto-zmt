import requests

def deepseek_api_call():
    api_url = "https://api.deepseek.com/v1/models"
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        print("API call successful")
        print(response.json())
    else:
        print("API call failed with status code:", response.status_code)

if __name__ == "__main__":
    deepseek_api_call()