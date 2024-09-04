import requests
import json

def analyze_curl_request():
    url = 'https://m.toutiao.com/list/?tag=__all__&max_time=1725409291&max_behot_time=1725409291&ac=wap&count=20&format=json_raw&_signature=oxib-wAAxdpfXCDdxPIW2KMYm-&i=1725409291&as=A116960D97ABEFA&cp=66D7EB3EAFCA6E1&aid=1698'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': '……',
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

    response = requests.get(url, headers=headers)
    data = response.json()

    # Analyze the parameters and return results
    print("URL Parameters:")
    print(url.split('?')[1])
    print("\nResponse Data:")
    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    analyze_curl_request()