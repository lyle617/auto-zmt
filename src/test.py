# 浏览器自动化工具
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
 
# 时间类
from time import sleep
 
from docx import Document
import pypandoc
 
 
if __name__ == '__main__':
    # 创建一个浏览器实例
    driver_path = "./chromedriver-mac-arm64/chromedriver"
    # 创建一个服务对象
    service = Service(driver_path)

    # 创建一个 Chrome 浏览器实例
    browser = webdriver.Chrome(service=service)
    # # 获取请求地址
    browser.get("https://toutiao.com/group/7405504703687115273")

    sleep(10)
 
    # 根据元素名称获取元素内容
    textContainer = browser.find_element(By.CLASS_NAME,"syl-article-base")
    articleHtml = textContainer.get_attribute("innerHTML")
 
    # 根据解析的HTML内容，获取文章文本信息和图片信息,并将文本信息和图片保存到Word文档中
    # file = open("E:\\studyproject\\python\\toutiao\data\\"+articleId+"\\"+articleId+".html", "r",encoding='utf-8')
    # os.mkdir("/tmp/"+articleId)
 
    output = pypandoc.convert_text(articleHtml, 'docx','html',outputfile="articles/7405504703687115273.docx")
 
    sleep(10)
    browser.quit()
 
