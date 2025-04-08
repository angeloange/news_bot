# NewsLingo

![NewsLingo](https://img.shields.io/badge/NewsLingo-多語言新聞與語言學習平台-blue)

NewsLingo 是一個結合新聞閱讀和英語學習的網頁應用程式，自動爬取 BBC 和台灣新聞，提供中英雙語內容與多益練習題，幫助使用者同時獲取資訊和提升語言能力。

## 主要功能

- 🌍 **國際新聞 (BBC)**: 自動爬取 BBC 最熱門閱讀與觀看新聞，並翻譯標題
- 🇹🇼 **台灣新聞**: 抓取 Google News 台灣版熱門新聞
- 📚 **多益練習**: 提供 TOEIC 閱讀練習題目，包含答案解析和詞彙表
- 💬 **對話式界面**: 直覺的聊天式使用者界面

## 技術特點

- 🚀 **高效爬蟲**: 使用 Playwright 無頭瀏覽器爬取動態內容
- 🔄 **批量翻譯**: OpenAI API 批量處理多個標題，提升效率
- ⚡ **性能優化**: 實現並行處理與資源快取，大幅提升響應速度
- 🌐 **公開部署**: 支援 ngrok 快速將本地服務公開至網路

## 如何安裝

```bash
# 克隆專案
git clone https://github.com/yourusername/news_bot.git
cd news_bot

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env 文件，添加 OpenAI API 金鑰

# 啟動應用
python app.py
