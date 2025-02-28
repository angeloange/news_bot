# filepath: /Users/angelo/Desktop/news_bot/utils/openai_helper.py
import os
import logging
import time
import openai
from openai import OpenAI
from dotenv import load_dotenv
import traceback
load_dotenv()
logger = logging.getLogger(__name__)

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_toeic_question(article_text):
    """基於文章生成多益閱讀題目"""
    try:
        logger.info("開始生成多益閱讀題目...")
        start_time = time.time()
        
        # 創建系統提示詞
        system_prompt = """
        你是一位專業的多益(TOEIC)閱讀題目出題者。
        請基於提供的英文文章，創建一個標準的多益閱讀測驗題目。
        要求:
        1. 保持文章原文不變
        2. 創建4個選擇題，每題4個選項(A-D)
        3. 問題應該測試閱讀理解能力，包括：主旨理解、細節掌握、推論能力和詞彙理解
        4. 提供答案和簡短的中文解釋
        5. 使用標準多益題目格式

        輸出格式:
        [TEXT] (保持原文不變)
        <原始文章>

        [QUESTIONS]
        1. <問題1>
           A. <選項A>
           B. <選項B>
           C. <選項C>
           D. <選項D>

        (問題2-4重複上述格式)

        [ANSWERS]
        1. <正確選項代號>: <中文解釋>
        2. <正確選項代號>: <中文解釋>
        3. <正確選項代號>: <中文解釋>
        4. <正確選項代號>: <中文解釋>
        """
        
        # 發送請求到 OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 或其他可用模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"請基於以下文章創建多益閱讀題目:\n\n{article_text}"}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # 取得回覆
        result = response.choices[0].message.content
        
        # 記錄執行時間
        elapsed = time.time() - start_time
        logger.info(f"多益題目生成完成，耗時: {elapsed:.2f}秒")
        
        return {
            "result": result,
            "execution_time": elapsed
        }
    
    except Exception as e:
        logger.error(f"生成多益題目時發生錯誤: {str(e)}")
        return {
            "error": str(e)
        }

def get_random_toeic_article():
    """獲取一篇隨機的適合多益閱讀練習的短文"""
    try:
        logger.info("獲取隨機多益閱讀文章...")
        start_time = time.time()
        
        # 創建系統提示詞
        system_prompt = """
        你是一位專業的多益(TOEIC)閱讀材料編寫者。
        請創建一篇適合多益閱讀測驗的英文短文。
        要求:
        1. 文章長度約150-200字
        2. 使用商務、職場或日常生活情境
        3. 難度應符合TOEIC閱讀測驗水準 (CEFR B1-B2)
        4. 題材可包括：公司內部郵件、商業通知、廣告、新聞簡報等
        5. 使用自然、專業的英文表達方式

        只需提供英文文章本身，不需要包含任何題目或解釋。
        """
        
        # 發送請求到 OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # 或其他可用模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "請創建一篇適合多益閱讀測驗的英文短文。"}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        # 取得回覆
        article = response.choices[0].message.content
        
        # 記錄執行時間
        elapsed = time.time() - start_time
        logger.info(f"文章生成完成，耗時: {elapsed:.2f}秒")
        
        return {
            "article": article,
            "execution_time": elapsed
        }
    
    except Exception as e:
        logger.error(f"生成文章時發生錯誤: {str(e)}")
        return {
            "error": str(e)
        }


import json

# 修改 translate_titles 函數

def translate_titles(titles):
    """批量將英文標題翻譯成中文"""
    if not titles or len(titles) == 0:
        return {}
    
    try:
        logger.info(f"開始批量翻譯 {len(titles)} 個標題...")
        start_time = time.time()
        
        # 去重並保持順序
        unique_titles = []
        seen = set()
        for title in titles:
            if title not in seen:
                unique_titles.append(title)
                seen.add(title)
        
        # 創建系統提示詞
        system_prompt = """
        你是一個專業的新聞標題翻譯員。請將以下英文新聞標題翻譯成中文。
        保持翻譯簡潔、準確，並符合中文新聞標題的風格。
        返回的結果應為 JSON 格式，鍵為原始英文標題，值為中文翻譯。
        """
        
        # 創建用戶提示詞，包含所有需要翻譯的標題
        user_prompt = "請將以下英文新聞標題翻譯成中文:\n\n"
        for i, title in enumerate(unique_titles):
            if title:
                # 清理標題中可能的編號
                clean_title = title
                if clean_title.strip().split(' ')[0].isdigit():
                    clean_title = ' '.join(clean_title.strip().split(' ')[1:])
                user_prompt += f"{i+1}. {clean_title}\n"
        
        user_prompt += "\n請以JSON格式返回翻譯結果，英文標題為鍵，中文翻譯為值。不要包含編號。"
        
        # 發送請求到 OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用較輕量的模型以節省成本
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        # 解析回應
        content = response.choices[0].message.content
        try:
            result = json.loads(content)
            
            # 確保所有標題都有對應的翻譯
            translations = {}
            for title in titles:
                clean_title = title
                if clean_title.strip().split(' ')[0].isdigit():
                    clean_title = ' '.join(clean_title.strip().split(' ')[1:])
                
                # 嘗試找到對應的翻譯
                if clean_title in result:
                    translations[title] = result[clean_title]
                else:
                    # 如果找不到，嘗試模糊匹配
                    matched = False
                    for k, v in result.items():
                        if clean_title.lower() in k.lower() or k.lower() in clean_title.lower():
                            translations[title] = v
                            matched = True
                            break
                    
                    if not matched:
                        translations[title] = ""
            
            # 記錄執行時間
            elapsed = time.time() - start_time
            logger.info(f"標題翻譯完成，耗時: {elapsed:.2f}秒")
            
            return translations
            
        except json.JSONDecodeError:
            logger.error("無法解析 OpenAI 返回的 JSON")
            logger.error(f"原始內容: {content}")
            return {}
        
    except Exception as e:
        logger.error(f"翻譯標題時發生錯誤: {str(e)}")
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        return {}

