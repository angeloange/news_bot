import pyshorteners
import logging
import concurrent.futures
logger = logging.getLogger(__name__)

def shorten_url(url):
    """將長網址縮短"""
    try:
        # 使用 TinyURL 服務
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(url)
        return short_url
    except Exception as e:
        logger.error(f"縮短網址時出錯: {e}")
        return url  # 如果失敗，返回原始網址

def shorten_urls_in_parallel(urls, max_workers=10):
    """並行縮短多個網址"""
    shortened = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(shorten_url, url): url for url in urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            original_url = future_to_url[future]
            try:
                shortened[original_url] = future.result()
            except Exception as e:
                logger.error(f"處理網址縮短時發生錯誤: {e}")
                shortened[original_url] = original_url
    
    return shortened

if __name__ == "__main__":
    # 測試縮短網址功能
    url = "https://www.example.com/very-long-url-with-lots-of-text"
    short_url = shorten_url(url)
    print(f"原始網址: {url}")
    print(f"縮短後: {short_url}")