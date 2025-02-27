from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def get_bbc_trending_news():
    # 設置 Chrome 選項
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    print("正在初始化瀏覽器...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 訪問網站
    url = "https://www.bbc.com/news"
    print(f"正在載入 {url}...")
    driver.get(url)
    
    # 等待頁面完全載入
    print("等待頁面加載...")
    time.sleep(3)
    
    # 保存完整的 HTML 供分析
    with open("bbc_complete.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("完整 HTML 已保存至 bbc_complete.html")
    
    # 尋找 Most Read 區塊（使用 XPath 或 CSS 選擇器）
    print("尋找熱門區塊...")
    
    trending_news = {
        'most_watched': [],
        'most_read': []
    }
    
    try:
        # 尋找 "Most watched"
        most_watched_elem = driver.find_elements(By.XPATH, "//h2[contains(text(), 'Most watched')]")
        if most_watched_elem:
            print("找到 Most Watched 區塊!")
            parent = most_watched_elem[0].find_element(By.XPATH, "./ancestor::section")
            links = parent.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    title = link.text.strip()
                    if title and "Most watched" not in title:
                        trending_news['most_watched'].append({
                            'title': title,
                            'url': link.get_attribute('href')
                        })
                except:
                    pass
        
        # 尋找 "Most read"
        most_read_elem = driver.find_elements(By.XPATH, "//h2[contains(text(), 'Most read')]")
        if most_read_elem:
            print("找到 Most Read 區塊!")
            parent = most_read_elem[0].find_element(By.XPATH, "./ancestor::section")
            links = parent.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    title = link.text.strip()
                    if title and "Most read" not in title:
                        trending_news['most_read'].append({
                            'title': title,
                            'url': link.get_attribute('href')
                        })
                except:
                    pass
                    
    except Exception as e:
        print(f"錯誤: {str(e)}")
    
    # 關閉瀏覽器
    driver.quit()
    
    return trending_news

if __name__ == "__main__":
    news = get_bbc_trending_news()
    
    print("\n=== Most Watched ===")
    if news['most_watched']:
        for i, item in enumerate(news['most_watched'], 1):
            print(f"{i}. {item['title']}")
            print(f"   連結: {item['url']}")
    else:
        print("未找到 Most Watched 內容")
    
    print("\n=== Most Read ===")
    if news['most_read']:
        for i, item in enumerate(news['most_read'], 1):
            print(f"{i}. {item['title']}")
            print(f"   連結: {item['url']}")
    else:
        print("未找到 Most Read 內容")
print("=== 爬蟲結束 ===")