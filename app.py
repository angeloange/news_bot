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

load_dotenv()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 導入爬蟲模組
from scrapers.bbc_scraper import get_bbc_trending_news

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
    
    # 處理國內新聞請求 (未實現)
    elif user_message.lower() in ["國內新聞", "台灣新聞", "2"]:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="國內新聞功能即將推出，敬請期待！")
        )
    
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
            # 取前 10 個，或所有項目如果少於 10 個
            most_read_items = news['most_read'][:10] if len(news['most_read']) > 10 else news['most_read']
            
            for i, item in enumerate(most_read_items, 1):
                # 添加標題和鏈接
                news_text += f"{item['title']}\n"
                news_text += f"{item['url']}\n\n"  # 添加連結並增加空行
            
            # 不需要額外空行，因為每個項目後已添加空行
        
        # 添加 Most Watched 新聞
        if news['most_watched']:
            news_text += "📺 最多觀看：\n"
            # 同樣取前 10 個，或所有項目如果少於 10 個
            most_watched_items = news['most_watched'][:10] if len(news['most_watched']) > 10 else news['most_watched']
            
            for i, item in enumerate(most_watched_items, 1):
                # 添加標題和鏈接
                news_text += f"{item['title']}\n"
                news_text += f"{item['url']}\n\n"  # 添加連結並增加空行
        
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
        

if __name__ == "__main__":
    # 在開發環境中使用
    app.run(debug=True, host='0.0.0.0', port=5004)