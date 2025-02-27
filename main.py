from scrapers.bbc_scraper import get_bbc_trending_news

def display_news(news_dict):
    """顯示新聞資料"""
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

def main():
    """主程序入口"""
    print("開始爬取 BBC 新聞...")
    news = get_bbc_trending_news()
    display_news(news)

if __name__ == "__main__":
    main()