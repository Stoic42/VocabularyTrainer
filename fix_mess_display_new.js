/**
 * 修复多词性多义项单词显示问题的脚本
 * 该脚本将重新设计错误历史和出题界面中词性和义项的显示逻辑
 */

// 格式化词性和意思的函数
function extractPOSAndMeaning(pos, meaning) {
    if (!pos && !meaning) {
        return { extractedPos: 'N/A', formattedMeaning: 'N/A' };
    }
    
    // 先将词性和中文意思连接起来
    const combinedText = pos && meaning ? pos + ' ' + meaning : (pos || meaning || '');
    
    // 这个正则表达式会找到所有的词性标签 (如 n./v./adj. 等)
    const posRegex = /\b(n|v|vt|vi|adj|adv|prep|conj|art|pron)\./g;
    
    // 提取combinedText中的所有词性
    const posMatches = combinedText ? [...combinedText.matchAll(posRegex)] : [];
    let extractedPos = '';
    
    if (posMatches.length > 0) {
        // 从combinedText中提取所有词性并用&连接，确保每个词性后面有'.'
        extractedPos = posMatches.map(match => match[1] + '.').join(' & ');
    }
    
    // 如果没有从combinedText中提取到词性，则使用传入的pos
    if (!extractedPos && pos) {
        extractedPos = pos;
    }
    
    // 处理中文意思的换行显示和词性标签添加
    let formattedMeaning = meaning;
    if (meaning) {
        // 找到所有词性标签的位置和内容
        const posInfo = [];
        let match;
        const regex = new RegExp(posRegex);
        let meaningCopy = meaning.slice();
        
        while ((match = regex.exec(meaningCopy)) !== null) {
            posInfo.push({
                index: match.index,
                pos: match[1] + '.',
                length: match[0].length
            });
        }
        
        // 如果有词性标签，处理换行和词性标签
        if (posInfo.length > 0) {
            // 将文本按词性分段
            let segments = [];
            
            // 处理多个词性的情况
            if (posInfo.length > 1) {
                for (let i = 0; i < posInfo.length; i++) {
                    const currentPos = posInfo[i];
                    let endIndex = i < posInfo.length - 1 ? posInfo[i + 1].index : meaning.length;
                    
                    // 提取当前词性后面的文本，直到下一个词性标签
                    let text = meaning.substring(currentPos.index + currentPos.length, endIndex).trim();
                    segments.push(currentPos.pos + ' ' + text);
                }
            } 
            // 处理只有一个词性的情况
            else {
                const pos = posInfo[0];
                let text = meaning.substring(pos.index + pos.length).trim();
                segments.push(pos.pos + ' ' + text);
            }
            
            // 用<br>连接所有段落
            formattedMeaning = segments.join('<br>');
        }
    }
    
    // 返回提取的词性和格式化后的中文意思
    return { extractedPos, formattedMeaning };
}

// 为了向后兼容，保留原始函数的调用方式
window.formatPOSAndMeaning = function(pos, meaning) {
    const result = extractPOSAndMeaning(pos, meaning);
    return result;
}

// 添加CSS样式
function addStyles() {
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .pos-tag {
            display: inline-block;
            padding: 2px 6px;
            margin-right: 5px;
            background-color: var(--pos-tag-bg, #e9ecef);
            color: var(--pos-tag-color, #495057);
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .meaning-item {
            margin-bottom: 4px;
        }
    `;
    document.head.appendChild(styleElement);
}

// 修复错误历史页面
function fixErrorHistoryPage() {
    console.log('正在修复错误历史页面...');
    
    // 在这里添加错误历史页面的修复逻辑
    // 例如，修改表格渲染、调整样式等
}

// 修复考核页面
function fixAssessmentPage() {
    console.log('正在修复考核页面...');
    
    // 在这里添加考核页面的修复逻辑
    // 例如，修改单词显示、调整样式等
}

// 将formatPOSAndMeaning函数添加到全局作用域
window.formatPOSAndMeaning = formatPOSAndMeaning;

// 在页面加载完成后执行修复
document.addEventListener('DOMContentLoaded', function() {
    // 添加样式
    addStyles();
    
    // 检测当前页面是错词界面还是考核界面
    const isErrorHistoryPage = window.location.pathname.includes('error-history');
    const isAssessmentPage = !isErrorHistoryPage; // 假设只有这两种页面
    
    if (isErrorHistoryPage) {
        fixErrorHistoryPage();
    }
    
    if (isAssessmentPage) {
        fixAssessmentPage();
    }
});