// 修改渲染 BBC 新聞的部分

// 在 renderBBCNews 函數中添加標題處理

function cleanTitle(title) {
    if (!title) return "";
    // 檢查標題是否以數字和空格開頭
    const match = title.match(/^\d+\s+(.*)/);
    if (match) {
        return match[1];  // 返回不包含數字前綴的部分
    }
    return title;
}

// 渲染 BBC 新聞
function renderBBCNews(data) {
    let html = `<div class="news-section"><h3>📰 BBC 熱門新聞</h3>`;
    
    // 最多閱讀
    if (data.most_read && data.most_read.length > 0) {
        html += `<h4>📚 最多閱讀：</h4><div class="news-list">`;
        
        data.most_read.forEach((item, index) => {
            // 清理標題，移除數字前綴
            const title = cleanTitle(item.title);
            
            html += `<div class="news-item">
                <div class="news-title">${title}</div>`; // 移除 ${index + 1}.
            
            if (item.translation) {
                html += `<div class="news-translation">【${item.translation}】</div>`;
            }
            
            html += `<a class="news-link" href="${item.url}" target="_blank">${item.url}</a>
            </div>`;
        });
        
        html += `</div>`;
    }
    
    // 最多觀看
    if (data.most_watched && data.most_watched.length > 0) {
        html += `<h4>📺 最多觀看：</h4><div class="news-list">`;
        
        data.most_watched.forEach((item, index) => {
            // 清理標題，移除數字前綴
            const title = cleanTitle(item.title);
            
            html += `<div class="news-item">
                <div class="news-title">${title}</div>`; // 移除 ${index + 1}.
            
            if (item.translation) {
                html += `<div class="news-translation">【${item.translation}】</div>`;
            }
            
            html += `<a class="news-link" href="${item.url}" target="_blank">${item.url}</a>
            </div>`;
        });
        
        html += `</div>`;
    }
    
    // 添加耗時資訊
    if (data.translation_time) {
        html += `<div class="timing-info">(資料更新耗時: ${(data.elapsed - data.translation_time).toFixed(1)}秒，翻譯耗時: ${data.translation_time.toFixed(1)}秒)</div>`;
    } else {
        html += `<div class="timing-info">(資料更新耗時: ${data.elapsed.toFixed(1)}秒)</div>`;
    }
    
    html += `</div>`;
    addBotMessage(html);
}