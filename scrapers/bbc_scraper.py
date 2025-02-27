from playwright.sync_api import sync_playwright
import time
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_bbc_trending_news():
    """獲取BBC新聞網站的熱門新聞"""
    start_time = time.time()
    trending_news = {
        'most_watched': [],
        'most_read': []
    }
    
    # 使用 Playwright 而非 Selenium
    with sync_playwright() as playwright:
        # 啟動瀏覽器 - 使用 chromium（啟動更快）
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # 阻擋圖片加載以提高速度
        context.route('**/*.{png,jpg,jpeg,webp,svg,gif}', lambda route: route.abort())
        
        # 創建新頁面
        page = context.new_page()
        
        try:
            # 訪問BBC新聞網站
            url = "https://www.bbc.com/news"
            logger.info(f"正在載入 {url}...")
            start_nav = time.time()
            page.goto(url, wait_until='domcontentloaded')
            
            # 等待頁面載入 (替代原來的固定3秒等待)
            logger.info("等待頁面加載...")
            page.wait_for_selector("h2, .most-read, .most-watched", timeout=5000)
            logger.info(f"頁面載入完成，耗時: {time.time()-start_nav:.2f}秒")
            
            # 保存完整的 HTML 供分析
            html_content = page.content()
            with open("bbc_complete.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("完整 HTML 已保存至 bbc_complete.html")
            
            # 尋找熱門區塊
            logger.info("尋找熱門區塊...")
            
            # 爬取 Most watched - 使用與原始代碼相同的邏輯
            most_watched = _extract_section_playwright(page, "Most watched")
            if most_watched:
                trending_news['most_watched'] = most_watched
                logger.info(f"成功獲取 {len(most_watched)} 個 Most watched 項目")
            
            # 爬取 Most read - 使用與原始代碼相同的邏輯
            most_read = _extract_section_playwright(page, "Most read")
            if most_read:
                trending_news['most_read'] = most_read
                logger.info(f"成功獲取 {len(most_read)} 個 Most read 項目")
            
        except Exception as e:
            logger.error(f"錯誤: {e}")
        finally:
            # 關閉瀏覽器
            browser.close()
    
    # 記錄執行時間
    elapsed = time.time() - start_time
    trending_news['execution_time'] = elapsed
    logger.info(f"BBC爬蟲耗時: {elapsed:.2f}秒")
    
    return trending_news

def _extract_section_playwright(page, section_title):
    """使用Playwright提取特定區塊的新聞（與原始邏輯相同但修復bug）"""
    results = []
    
    try:
        # 使用等同於Selenium版本的XPath查詢
        section_elems = page.query_selector_all(f"xpath=//h2[contains(text(), '{section_title}')]")
        
        if section_elems and len(section_elems) > 0:
            logger.info(f"找到 {section_title} 區塊!")
            
            # 找到祖先section元素 - 修復：確保parent是元素對象而非字符串
            parent = None
            try:
                # 使用JS的closest函數尋找最近的section祖先
                parent_element = section_elems[0].evaluate("node => { const parent = node.closest('section'); return parent ? parent : null; }")
                if parent_element:
                    # 如果找到了section父元素，使用它
                    parent = page.evaluate_handle(f"document.querySelector('[data-component=\"most-{section_title.lower().split()[1]}\"]')").as_element()
                    if not parent:
                        # 如果找不到特定組件，使用section元素自己的父級找到section
                        parent = section_elems[0].evaluate_handle("node => node.closest('section')").as_element()
            except Exception as e:
                logger.error(f"找到section父元素時出錯: {e}")
                
            # 如果找到了父元素，繼續處理
            if parent:
                # 找到所有鏈接
                links = parent.query_selector_all("a")
                logger.info(f"在 {section_title} 區塊中找到 {len(links)} 個鏈接")
                
                for link in links:
                    try:
                        title = link.inner_text().strip()
                        href = link.get_attribute("href")
                        
                        # 處理相對URL
                        if href and href.startswith("/"):
                            href = f"https://www.bbc.com{href}"
                        
                        if title and section_title not in title:
                            results.append({
                                'title': title,
                                'url': href
                            })
                    except Exception as e:
                        logger.debug(f"處理鏈接時出錯: {e}")
    except Exception as e:
        logger.error(f"提取 {section_title} 區塊時出錯: {e}")
    
    return results

if __name__ == "__main__":
    start_time = time.time()
    news = get_bbc_trending_news()
    elapsed = time.time() - start_time
    
    print(f"\n總執行耗時: {elapsed:.2f}秒")
    
    print("\n=== Most Read ===")
    if news['most_read']:
        for i, item in enumerate(news['most_read'], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['url']}")
    else:
        print("未找到 Most Read 內容")
    
    print("\n=== Most Watched ===")
    if news['most_watched']:
        for i, item in enumerate(news['most_watched'], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['url']}")
    else:
        print("未找到 Most Watched 內容")