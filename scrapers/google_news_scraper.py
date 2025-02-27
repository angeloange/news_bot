from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import concurrent.futures
import time
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_real_url(google_url):
    """獲取 Google News 重定向後的真實URL"""
    try:
        response = requests.head(google_url, allow_redirects=True, timeout=2)
        return response.url
    except Exception:
        return google_url

def process_urls_in_parallel(urls, max_workers=15):
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

def get_google_news_taiwan(max_news=10):
    """獲取Google News台灣版新聞"""
    news_list = []
    google_urls = []

    # 使用 Playwright 而非 Selenium
    with sync_playwright() as playwright:
        # 啟動瀏覽器 - 使用 chromium（啟動更快）
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # 創建新頁面
        page = context.new_page()
        
        try:
            # 訪問Google News台灣版
            url = "https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRFptTXpJU0JYcG9MVlJYS0FBUAE?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant"
            logger.info(f"正在載入 Google News 台灣版...")
            start_nav = time.time()
            page.goto(url, wait_until='domcontentloaded')
            
            # 等待文章元素出現
            page.wait_for_selector("article", timeout=5000)
            logger.info(f"頁面載入完成，耗時: {time.time()-start_nav:.2f}秒")
            
            # 獲取頁面內容
            html_content = page.content()
            
        except Exception as e:
            logger.error(f"獲取頁面時出錯: {e}")
            return news_list
        finally:
            browser.close()
    
        # 使用BeautifulSoup解析
        soup = BeautifulSoup(html_content, "lxml")
        
        # 定位新聞文章
        articles = soup.select("article")[:max_news]
        logger.info(f"找到 {len(articles)} 個新聞")
        
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
                logger.error(f"解析新聞 #{i} 時出錯: {e}")
        
        # 第二步：並行獲取所有重定向URL
        if google_urls:
            logger.info(f"開始並行處理 {len(google_urls)} 個URL重定向...")
            start_time = time.time()
            real_url_map = process_urls_in_parallel(google_urls,max_workers=15)
            elapsed = time.time() - start_time
            logger.info(f"URL重定向處理完成，耗時: {elapsed:.2f}秒")
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
                
        # 最後添加執行時間到結果中
        elapsed = time.time() - start_time
        logger.info(f"Google News抓取完成，共找到 {len(news_list)} 個新聞，耗時: {elapsed:.2f}秒")
        
        # 用一個特殊的字典格式封裝結果
        return {
            "news": news_list,
            "execution_time": elapsed
        }

