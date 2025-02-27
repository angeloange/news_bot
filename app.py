from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    QuickReply, QuickReplyButton, MessageAction
)
import os
import logging
import time
from dotenv import load_dotenv
from utils.url_shortener import shorten_url, shorten_urls_in_parallel


load_dotenv()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 導入爬蟲模組
from scrapers.bbc_scraper import get_bbc_trending_news
from scrapers.google_news_scraper import get_google_news_taiwan  # 添加這行

app = Flask(__name__)

# 設置 LINE Bot API
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN' ))  # 請替換為你的token
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET') )  # 請替換為你的secret

@app.route("/callback", methods=['POST'])
def callback():
    """LINE Bot Webhook 回調函數"""
    # 獲取 X-Line-Signature 頭部值
    signature = request.headers['X-Line-Signature']

    # 獲取請求正文文本
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)

    # 驗證簽名
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)

    return 'OK'

@app.route("/", methods=['GET'])
def hello():
    """提供簡單的首頁回應，用於檢查服務是否正常運行"""
    return 'NewsCoach by Angelo - LINE Bot is running!'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理用戶發送的文字訊息"""
    user_message = event.message.text.strip()
    
    # 主選單
    if user_message.lower() in ["help", "menu", "選單", "幫助", "hi", "hello", "嗨", "你好"]:
        show_main_menu(event.reply_token)
    
    # 處理BBC新聞請求
    elif user_message.lower() in ["bbc", "國外新聞", "1"]:
        send_bbc_news(event.reply_token)
    
    # 處理國內新聞請求 (使用 Google News)
    elif user_message.lower() in ["國內新聞", "台灣新聞", "2"]:
        send_google_news(event.reply_token)
    
    # 處理多益閱讀請求 (未實現)
    elif user_message.lower() in ["多益", "toeic", "3"]:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="多益閱讀題目功能即將推出，敬請期待！")
        )
    
    # 默認回覆
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我不太明白你的意思。請輸入「選單」來查看可用選項。")
        )

def show_main_menu(reply_token):
    """顯示主選單"""
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(
            text="📰 歡迎使用 NewsCoach by Angelo！\n請選擇服務：",
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="國外新聞", text="國外新聞(BBC)")),
                QuickReplyButton(action=MessageAction(label="國內新聞", text="國內新聞")),
                QuickReplyButton(action=MessageAction(label="多益閱讀題目", text="多益"))
            ])
        )
    )

def send_bbc_news(reply_token):
    """發送 BBC 新聞"""
    try:
        logger.info("開始獲取 BBC 新聞...")
        start_time = time.time()
        
        # 調用 BBC 爬蟲
        news = get_bbc_trending_news()
        
        # 格式化回覆訊息
        news_text = "📰 BBC 熱門新聞：\n\n"
        
        # 添加 Most Read 新聞
        if news['most_read']:
            news_text += "📚 最多閱讀：\n"
            # 取前 5 個，或所有項目如果少於 5 個
            most_read_items = news['most_read'][:5] if len(news['most_read']) > 5 else news['most_read']
            
            for i, item in enumerate(most_read_items, 1):
                # 移除標題中可能存在的編號
                title = item['title']
                # 檢查標題是否以數字和點開頭，如果是則去除
                if title and title[0].isdigit() and len(title) > 1:
                    # 找到第一個非數字字符的位置
                    pos = 0
                    while pos < len(title) and (title[pos].isdigit() or title[pos] in '. '):
                        pos += 1
                    title = title[pos:].strip()
                    
                # 添加標題和鏈接
                news_text += f"{i}. {title}\n"
                news_text += f"   {item['url']}\n\n"  # 添加連結並增加空行
        
        # 添加 Most Watched 新聞
        if news['most_watched']:
            news_text += "📺 最多觀看：\n"
            most_watched_items = news['most_watched'][:5] if len(news['most_watched']) > 5 else news['most_watched']
            
            for i, item in enumerate(most_watched_items, 1):
                # 移除標題中可能存在的編號
                title = item['title']
                # 檢查標題是否以數字和點開頭，如果是則去除
                if title and title[0].isdigit() and len(title) > 1:
                    # 找到第一個非數字字符的位置
                    pos = 0
                    while pos < len(title) and (title[pos].isdigit() or title[pos] in '. '):
                        pos += 1
                    title = title[pos:].strip()
                
                # 添加標題和鏈接
                news_text += f"{i}. {title}\n"
                news_text += f"   {item['url']}\n\n"  # 添加連結並增加空行
        
        # 添加執行時間資訊
        elapsed = time.time() - start_time
        news_text += f"(資料更新耗時: {elapsed:.1f}秒)"
        
        # 檢查消息是否過長 (LINE 限制單條消息最多 5000 字元)
        if len(news_text) > 5000:
            news_text = news_text[:4900] + "...\n\n(消息過長，已截斷)"
        
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=news_text)
        )
        
        logger.info(f"BBC 新聞發送成功，耗時: {elapsed:.2f}秒")
    except Exception as e:
        logger.error(f"獲取BBC新聞時出現錯誤: {str(e)}")
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"抱歉，獲取BBC新聞時出現錯誤：{str(e)}")
        )
        
def send_google_news(reply_token):
    """發送 Google News 台灣新聞"""
    try:
        logger.info("開始獲取 Google News 台灣新聞...")
        start_time = time.time()
        
        # 調用 Google News 爬蟲
        news_data = get_google_news_taiwan(max_news=10)  # 減少為10條提升效能
        
        # 準備縮短網址
        news_list = news_data.get('news', [])
        if news_list:
            # 收集所有 URL
            urls_to_shorten = [item['url'] for item in news_list]
            
            # 並行縮短所有 URL
            logger.info(f"開始縮短 {len(urls_to_shorten)} 個網址...")
            url_shorten_start = time.time()
            shortened_urls = shorten_urls_in_parallel(urls_to_shorten)
            url_shorten_time = time.time() - url_shorten_start
            logger.info(f"網址縮短完成，耗時: {url_shorten_time:.2f}秒")
        
        # 格式化回覆訊息
        news_text = "📰 Google News 台灣熱門新聞：\n\n"
        
        # 添加新聞
        if news_list:
            for i, item in enumerate(news_list, 1):
                # 添加標題和鏈接
                news_text += f"{i}. {item['title']}\n"
                # 使用已縮短的網址
                short_url = shortened_urls.get(item['url'], item['url'])
                news_text += f"   {short_url}\n\n"
        else:
            news_text += "未找到任何新聞項目。\n"
            
        # 添加執行時間資訊
        elapsed = time.time() - start_time
        news_text += f"(資料更新耗時: {elapsed:.1f}秒)"
        
        # 檢查消息是否過長 (LINE 限制單條消息最多 5000 字元)
        if len(news_text) > 5000:
            news_text = news_text[:4900] + "...\n\n(消息過長，已截斷)"
        
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=news_text)
        )
        
        logger.info(f"Google News 台灣新聞發送成功，耗時: {elapsed:.2f}秒")
    except Exception as e:
        logger.error(f"獲取 Google News 台灣新聞時出現錯誤: {str(e)}")
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"抱歉，獲取台灣新聞時出現錯誤：{str(e)}")
        )

if __name__ == "__main__":
    # 在開發環境中使用
    app.run(debug=True, host='0.0.0.0', port=5004)