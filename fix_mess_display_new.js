/**
 * 修复多词性多义项单词显示问题的脚本
 * 该脚本将重新设计错误历史和出题界面中词性和义项的显示逻辑
 */

// 格式化词性和意思的函数
function formatPOSAndMeaning(pos, meaning) {
    if (!pos && !meaning) {
        return 'N/A';
    }
    if (!pos) {
        return meaning;
    }
    
    // 检查meaning是否以词性标签开头
    const startsWithPOS = /^(n|v|vt|vi|adj|adv|prep|conj|art|pron)\./i.test(meaning);
    
    // 这个正则表达式会找到所有的词性标签 (如 n./v./adj. 等)
    const posRegex = /\b(n|v|vt|vi|adj|adv|prep|conj|art|pron)\./g;
    
    // 如果meaning以词性标签开头，先添加一个特殊标记
    let processedMeaning = startsWithPOS ? '|||' + meaning : meaning;
    
    // 用 "|||" 这个特殊标记替换所有词性标签，为下一步分割做准备
    const stringWithSeparator = processedMeaning.replace(posRegex, '|||$&');

    // 用 "|||" 分割字符串，得到包含词性和对应意思的数组
    const parts = stringWithSeparator.split('|||').filter(part => part.trim() !== '');

    if (parts.length <= 1) {
        // 如果只有一个词性或没有，就按原样显示
        return `<strong>${pos}</strong> ${meaning}`;
    }

    // 如果有多个词性，就进行换行处理
    return parts.map(part => {
        const subParts = part.trim().split(/\s+/);
        const currentPos = subParts[0];
        const currentMeaning = subParts.slice(1).join(' ');
        return `<strong>${currentPos}</strong> ${currentMeaning}`;
    }).join('<br>'); // 用 <br> 标签进行换行
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