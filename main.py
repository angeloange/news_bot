from scrapers.bbc_scraper import get_bbc_trending_news
from scrapers.google_news_scraper import get_google_news_taiwan
import sys
import time

def display_news(news_dict, source="bbc"):
    """顯示新聞資料"""
    if source == "bbc":
        # 顯示執行時間
        print(f"\n執行總耗時: {news_dict.get('execution_time', '未記錄')}秒")
        
        print("\n=== Most Watched ===")
        if news_dict['most_watched']:
            for i, item in enumerate(news_dict['most_watched'], 1):
                print(f"{i}. {item['title']}")
                print(f"   連結: {item['url']}")
        else:
            print("未找到 Most Watched 內容")
        
        print("\n=== Most Read ===")
        if news_dict['most_read']:
            for i, item in enumerate(news_dict['most_read'], 1):
                print(f"{i}. {item['title']}")
                print(f"   連結: {item['url']}")
        else:
            print("未找到 Most Read 內容")
    elif source == "google":
        # 顯示執行時間
        print(f"\n執行總耗時: {news_dict.get('execution_time', '未記錄')}秒")
        
        print("\n=== Google News 台灣熱門新聞 ===")
        news_items = news_dict.get('news', [])
        if news_items:
            for i, item in enumerate(news_items, 1):
                print(f"{i}. {item['title']}")
                print(f"   連結: {item['url']}")
                print()
        else:
            print("未找到任何新聞")

def main():
    """主程序入口"""
    if len(sys.argv) > 1 and sys.argv[1] == "google":
        print("開始爬取 Google News 台灣版...")
        news = get_google_news_taiwan()
        display_news(news, "google")
    else:
        print("開始爬取 BBC 新聞...")
        news = get_bbc_trending_news()
        display_news(news, "bbc")

if __name__ == "__main__":
    start_time = time.time()
    main()
    # 移除這裡的重複執行代碼，避免執行兩次
    elapsed = time.time() - start_time
    print(f"\n總耗時: {elapsed:.2f}秒")