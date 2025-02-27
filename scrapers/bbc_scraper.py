from selenium.webdriver.common.by import By
import time
from utils.browser_manager import initialize_browser

def get_bbc_trending_news():
    """獲取BBC新聞網站的熱門新聞"""
    driver = initialize_browser()
    
    trending_news = {
        'most_watched': [],
        'most_read': []
    }
    
    try:
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
        
        # 尋找熱門區塊
        print("尋找熱門區塊...")
        
        # 爬取 Most watched
        most_watched = _extract_section(driver, "Most watched")
        if most_watched:
            trending_news['most_watched'] = most_watched
        
        # 爬取 Most read
        most_read = _extract_section(driver, "Most read")
        if most_read:
            trending_news['most_read'] = most_read
            
    except Exception as e:
        print(f"錯誤: {str(e)}")
    finally:
        # 關閉瀏覽器
        driver.quit()
    
    return trending_news

def _extract_section(driver, section_title):
    """提取特定區塊的新聞（輔助函數）"""
    results = []
    section_elem = driver.find_elements(By.XPATH, f"//h2[contains(text(), '{section_title}')]")
    
    if section_elem:
        print(f"找到 {section_title} 區塊!")
        parent = section_elem[0].find_element(By.XPATH, "./ancestor::section")
        links = parent.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            try:
                title = link.text.strip()
                if title and section_title not in title:
                    results.append({
                        'title': title,
                        'url': link.get_attribute('href')
                    })
            except:
                pass
    
    return results