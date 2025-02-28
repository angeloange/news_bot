import traceback
import os
import time
import json
import random
import logging
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv

# 自定義模組
from utils.url_shortener import shorten_urls_in_parallel
from utils.openai_helper import translate_titles
from scrapers.bbc_scraper import get_bbc_trending_news
from scrapers.google_news_scraper import get_google_news_taiwan

load_dotenv()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建 Flask 應用
app = Flask(__name__)

# 設置模板和靜態文件路徑
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# 網頁主頁
@app.route("/", methods=['GET'])
def web_interface():
    """提供網頁界面"""
    return render_template('index.html')

# API 端點 - 處理來自網頁的請求
@app.route("/api/message", methods=['POST'])
def process_web_message():
    """處理來自網頁的消息"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': '訊息不能為空'}), 400
        
        # 根據用戶消息執行相應操作
        if user_message.lower() in ["help", "menu", "選單", "幫助", "hi", "hello", "嗨", "你好"]:
            return jsonify({
                'type': 'menu',
                'title': '📰 歡迎使用 NewsLingo by Angelo！',
                'options': [
                    {'label': '國外新聞', 'value': '國外新聞(BBC)'},
                    {'label': '國內新聞', 'value': '國內新聞'},
                    {'label': '多益閱讀題目', 'value': '多益閱讀題目'}
                ]
            })
        elif user_message.lower() in ["bbc", "國外新聞", "1", "國外新聞(bbc)"]:
            return get_bbc_news_web()
        elif user_message.lower() in ["國內新聞", "台灣新聞", "2"]:
            return get_google_news_web()
        elif user_message.lower() in ["多益", "toeic", "3", "多益閱讀題目"]:
            return get_toeic_question_web()
        else:
            return jsonify({
                'type': 'text',
                'content': "我不太明白你的意思。請輸入「選單」來查看可用選項。"
            })
    except Exception as e:
        logger.error(f"處理網頁請求時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'處理請求時發生錯誤: {str(e)}'}), 500

# 修改 get_bbc_news_web 函數中處理翻譯的部分

def get_bbc_news_web():
    """網頁版 BBC 新聞"""
    try:
        logger.info("開始獲取 BBC 新聞 (網頁版)...")
        start_time = time.time()
        
        news = get_bbc_trending_news()
        titles_to_translate = []
        title_map = {}  # 用於儲存標題映射
        
        most_read_items = []
        if news['most_read']:
            most_read_items = news['most_read'][:5] if len(news['most_read']) > 5 else news['most_read']
            for i, item in enumerate(most_read_items):
                if item.get('title'):
                    clean_title = item['title']
                    # 如果有數字前綴，清除它
                    if clean_title.strip().split(' ')[0].isdigit():
                        clean_title = ' '.join(clean_title.strip().split(' ')[1:])
                    titles_to_translate.append(clean_title)
                    title_map[clean_title] = item['title']  # 保存映射
        
        most_watched_items = []
        if news['most_watched']:
            most_watched_items = news['most_watched'][:5] if len(news['most_watched']) > 5 else news['most_watched']
            for i, item in enumerate(most_watched_items):
                if item.get('title'):
                    clean_title = item['title']
                    # 如果有數字前綴，清除它
                    if clean_title.strip().split(' ')[0].isdigit():
                        clean_title = ' '.join(clean_title.strip().split(' ')[1:])
                    titles_to_translate.append(clean_title)
                    title_map[clean_title] = item['title']  # 保存映射
        
        # 批量翻譯標題
        translations = {}
        translation_time = 0
        if titles_to_translate:
            translation_start = time.time()
            translations_result = translate_titles(titles_to_translate)
            translation_time = time.time() - translation_start
            
            # 將翻譯結果映射回原始標題
            for clean_title, original_title in title_map.items():
                if clean_title in translations_result:
                    translations[original_title] = translations_result[clean_title]
        
        # 格式化最多閱讀新聞
        most_read_formatted = []
        for item in most_read_items:
            title = item.get('title', '')
            url = item.get('url', '#')
            translation = translations.get(title, '')
            most_read_formatted.append({
                'title': title,
                'url': url,
                'translation': translation
            })
        
        # 格式化最多觀看新聞
        most_watched_formatted = []
        for item in most_watched_items:
            title = item.get('title', '')
            url = item.get('url', '#')
            translation = translations.get(title, '')
            most_watched_formatted.append({
                'title': title,
                'url': url,
                'translation': translation
            })
        
        # 計算執行時間
        elapsed = time.time() - start_time
        
        return jsonify({
            'type': 'bbc_news',
            'most_read': most_read_formatted,
            'most_watched': most_watched_formatted,
            'elapsed': round(elapsed, 1),
            'translation_time': round(translation_time, 1)
        })
    except Exception as e:
        logger.error(f"獲取BBC新聞時出現錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'獲取BBC新聞時出現錯誤: {str(e)}'}), 500


# 網頁版 Google News 台灣新聞
def get_google_news_web():
    """網頁版 Google News 台灣新聞"""
    try:
        logger.info("開始獲取 Google News 台灣新聞 (網頁版)...")
        start_time = time.time()
        news_data = get_google_news_taiwan(max_news=10)
        news_list = news_data.get('news', [])
        
        # 準備縮短網址
        shortened_urls = {}
        if news_list:
            urls_to_shorten = [item['url'] for item in news_list]
            shortened_urls = shorten_urls_in_parallel(urls_to_shorten)
        
        # 格式化新聞列表
        formatted_news = []
        for item in news_list:
            title = item.get('title', '')
            url = item.get('url', '#')
            short_url = shortened_urls.get(url, url)
            formatted_news.append({
                'title': title,
                'url': short_url
            })
        
        # 計算執行時間
        elapsed = time.time() - start_time
        
        return jsonify({
            'type': 'google_news',
            'news': formatted_news,
            'elapsed': round(elapsed, 1)
        })
    except Exception as e:
        logger.error(f"獲取Google新聞時出現錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'獲取Google新聞時出現錯誤: {str(e)}'}), 500

# 網頁版多益閱讀題目
def get_toeic_question_web():
    """網頁版多益閱讀題目"""
    try:
        logger.info("開始獲取多益閱讀題目 (網頁版)...")
        start_time = time.time()
        
        # 載入 JSON 檔案
        with open('data/toeic_articles.json', 'r', encoding='utf-8') as file:
            articles = json.load(file)
        
        # 隨機選擇一篇文章
        article = random.choice(articles)
        
        # 格式化回傳資料
        result = {
            'type': 'toeic',
            'title': article['title'],
            'text': article['text'],
            'questions': article['questions'],
            'answers': article['answers'],
            'vocabulary': article['vocabulary'],
            'elapsed': round(time.time() - start_time, 1)
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"獲取多益題目時出現錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'獲取多益題目時出現錯誤: {str(e)}'}), 500

# 確保目錄存在的函數
def ensure_directories_exist():
    """確保必要的目錄結構存在"""
    directories = [
        os.path.join(os.path.dirname(__file__), 'templates'),
        os.path.join(os.path.dirname(__file__), 'static'),
        os.path.join(os.path.dirname(__file__), 'static', 'css'),
        os.path.join(os.path.dirname(__file__), 'static', 'js')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

# 添加 ngrok 支持
def setup_ngrok():
    """設置 ngrok 隧道"""
    try:
        from pyngrok import ngrok
        
        # 啟動 ngrok 隧道
        port = int(os.getenv('PORT', 5004))
        public_url = ngrok.connect(port)
        logger.info(f"* ngrok 隧道已建立: {public_url}")
        print(f"\n✅ ngrok 隧道已建立!")
        print(f"🌎 公開網址: {public_url}")
        print(f"🖥️ 網頁介面: {public_url}/\n")
        return True
    except ImportError:
        print("\n❌ 需要安裝 pyngrok 才能使用 ngrok 功能")
        print("📦 請執行: pip install pyngrok")
        return False
    except Exception as e:
        logger.error(f"啟動 ngrok 時出錯: {e}")
        print(f"\n❌ 啟動 ngrok 時出錯: {e}")
        return False

# 添加爛梗 API 路由

@app.route("/data/jokes", methods=['GET'])
def get_jokes():
    """提供爛梗數據"""
    try:
        # 嘗試讀取爛梗 JSON 文件
        try:
            with open('data/jokes.json', 'r', encoding='utf-8') as file:
                jokes = json.load(file)
                return jsonify(jokes)
        except FileNotFoundError:
            # 如果文件不存在，返回默認爛梗
            default_jokes = [
                "正在努力讀取新聞，請稍候...",
                "新聞比想像中難找，再等一下下...",
                "翻譯中...我的英文勉勉強強啦",
                "資料處理中，CPU 快燒起來了...",
                "請稍等，正在思考人生的意義..."
            ]
            return jsonify(default_jokes)
    except Exception as e:
        logger.error(f"獲取爛梗時出現錯誤: {str(e)}")
        return jsonify(["正在處理中，請稍候..."]), 500

if __name__ == "__main__":
    # 確保目錄存在
    ensure_directories_exist()
    
    # 檢查是否使用 ngrok
    use_ngrok = os.getenv('USE_NGROK', 'false').lower() == 'true'
    if use_ngrok:
        setup_ngrok()
    
    # 啟動 Flask 應用
    port = int(os.getenv('PORT', 5004))
    app.run(debug=True, host='0.0.0.0', port=port)