from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.browser_manager import initialize_browser
from bs4 import BeautifulSoup
import requests
import concurrent.futures
import time

def get_real_url(google_url):
    """獲取 Google News 重定向後的真實URL"""
    try:
        response = requests.head(google_url, allow_redirects=True, timeout=2)
        return response.url
    except Exception:
        return google_url

def process_urls_in_parallel(urls, max_workers=10):
    """並行處理多個URL的重定向"""
    real_urls = {}
    
    def process_url(url):
        real_url = get_real_url(url)
        return url, real_url
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            url, real_url = future.result()
            real_urls[url] = real_url
    
    return real_urls

def get_google_news_taiwan(max_news=15):
    """獲取Google News台灣版新聞"""
    driver = initialize_browser()
    news_list = []
    google_urls = []
    
    try:
        # 訪問Google News台灣版
        url = "https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRFptTXpJU0JYcG9MVlJYS0FBUAE?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant"
        print(f"正在載入 Google News 台灣版...")
        driver.get(url)
        
        # 使用顯式等待而非固定時間
        try:
            # 等待文章元素出現
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
            )
        except Exception:
            print("等待超時，繼續處理...")
        
        # 獲取並保存HTML
        html_content = driver.page_source
        
    except Exception as e:
        print(f"獲取頁面時出錯: {str(e)}")
        return news_list
    finally:
        driver.quit()
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(html_content, "lxml")
    
    # 更精確地定位新聞文章
    articles = soup.select("article")
    print(f"找到 {len(articles)} 個新聞")
    
    # 第一步：收集所有Google News URL
    temp_results = []
    for i, article in enumerate(articles[:max_news]):
        try:
            # 找標題 - 使用更精確的選擇器
            title_link = article.select_one("a.gPFEn, a.DY5T1d")
            if not title_link:
                continue
                
            # 提取標題
            title = title_link.text.strip()
            
            # 提取URL
            href = title_link.get("href")
            if href.startswith("./"):
                url = f"https://news.google.com{href[1:]}"
            elif href.startswith("/"):
                url = f"https://news.google.com{href}"
            else:
                url = href
                
            # 收集需要重定向的URL
            if "news.google.com" in url:
                google_urls.append(url)
            
            # 添加到臨時結果
            temp_results.append({
                "title": title,
                "google_url": url,
            })
            
        except Exception as e:
            print(f"解析新聞 #{i} 時出錯: {str(e)}")
    
    # 第二步：並行獲取所有重定向URL
    if google_urls:
        print(f"開始並行處理 {len(google_urls)} 個URL重定向...")
        start_time = time.time()
        real_url_map = process_urls_in_parallel(google_urls)
        elapsed = time.time() - start_time
        print(f"URL重定向處理完成，耗時: {elapsed:.2f}秒")
    else:
        real_url_map = {}
    
    # 第三步：生成最終結果
    for item in temp_results:
        google_url = item["google_url"]
        # 如果是Google News URL，使用重定向後的URL
        real_url = real_url_map.get(google_url, google_url)
        
        news_list.append({
            "title": item["title"],
            "url": real_url,
        })
            
    return news_list

if __name__ == "__main__":
    start_time = time.time()
    news = get_google_news_taiwan(15)
    elapsed = time.time() - start_time
    
    print(f"\n執行總耗時: {elapsed:.2f}秒")
    print(f"獲取 {len(news)} 則新聞:")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")
        print(f"   {item['url']}")
        print()