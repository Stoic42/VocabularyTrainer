/**
 * 修复多词性多义项单词显示问题的脚本
 * 该脚本将重新设计错误历史和出题界面中词性和义项的显示逻辑
 */

// 格式化词性和意思的函数
function extractPOSAndMeaning(pos, meaning) {
    if (!pos && !meaning) {
        return { extractedPos: 'N/A', formattedMeaning: 'N/A' };
    }
    
    // 检查原始数据是否完整
    // 如果pos中包含多个词性但meaning中只有部分词性的中文意思，尝试补全
    let processedMeaning = meaning;
    if (pos && meaning) {
        // 从pos中提取所有词性
        const posRegexForExtract = /\b(n|v|vt|vi|adj|adv|prep|conj|art|pron|aux|abbr|num|interj|sing|det|modal|inf|prefix|suffix|phrase|idiom)\.\s*(?:&\s*)?/g;
        const posMatches = [...pos.matchAll(posRegexForExtract)].map(match => match[1] + '.');
        
        // 检查meaning中是否包含所有词性的中文意思
        for (const posTag of posMatches) {
            // 如果meaning中不包含该词性标签，尝试添加
            if (!meaning.includes(posTag)) {
                // 查找meaning中是否有其他词性的中文意思
                const meaningPosRegex = new RegExp(`\\b(n|v|vt|vi|adj|adv|prep|conj|art|pron|aux|abbr|num|interj|pl|sing|det|modal|inf|prefix|suffix|phrase|idiom)\\.`, 'g');
                const meaningPosMatches = [...meaning.matchAll(meaningPosRegex)];
                
                if (meaningPosMatches.length > 0) {
                    // 如果meaning中有其他词性的中文意思，在开头添加缺失的词性标签
                    processedMeaning = posTag + ' ' + meaning;
                }
            }
        }
    }
    
    // 先将词性和中文意思连接起来
    const combinedText = pos && processedMeaning ? pos + ' ' + processedMeaning : (pos || processedMeaning || '');
    
    // 这个正则表达式会找到所有的词性标签 (如 n./v./adj./aux./abbr. 等)
    const posRegex = /\b(n|v|vt|vi|adj|adv|prep|conj|art|pron|aux|abbr|num|interj|sing|det|modal|inf|prefix|suffix|phrase|idiom)\./g;
    
    // 提取combinedText中的所有词性
    const posMatches = combinedText ? [...combinedText.matchAll(posRegex)] : [];
    let extractedPos = '';
    
    if (posMatches.length > 0) {
        // 从combinedText中提取所有词性并用&连接，确保每个词性后面有'.'
        // 使用Set去重，避免出现重复的词性
        const uniquePosSet = new Set(posMatches.map(match => match[1]));
        extractedPos = Array.from(uniquePosSet).map(pos => pos + '.').join(' & ');
    }
    
    // 如果没有从combinedText中提取到词性，则使用传入的pos
    if (!extractedPos && pos) {
        extractedPos = pos;
    }
    
    // 处理中文意思的换行显示和词性标签添加
    let formattedMeaning = processedMeaning;
    if (processedMeaning) {
        // 预处理：检查是否有方括号中的词性标签，如 [pl.]，这些不应该导致换行
        // 将方括号中的内容临时替换为不会被识别为词性标签的内容
        const bracketRegex = /\[(.*?)\]/g;
        const bracketContents = [];
        let bracketMatch;
        let tempMeaning = processedMeaning;
        
        while ((bracketMatch = bracketRegex.exec(processedMeaning)) !== null) {
            bracketContents.push(bracketMatch[0]);
            // 替换为一个不会被词性正则匹配的占位符
            tempMeaning = tempMeaning.replace(bracketMatch[0], `__BRACKET_${bracketContents.length - 1}__`);
        }
        
        // 找到所有词性标签的位置和内容（排除方括号中的内容）
        const posInfo = [];
        let match;
        const regex = new RegExp(posRegex);
        let meaningCopy = tempMeaning.slice();
        
        while ((match = regex.exec(meaningCopy)) !== null) {
            // 检查是否已经存在相同的词性标签，避免重复
            const existingPosIndex = posInfo.findIndex(info => info.pos === match[1] + '.');
            if (existingPosIndex === -1) {
                posInfo.push({
                    index: match.index,
                    pos: match[1] + '.',
                    length: match[0].length
                });
            }
        }
        
        // 如果没有找到词性标签，但pos字段有值，在开头添加词性
        if (posInfo.length === 0 && pos && pos.trim()) {
            const extractedPos = pos.trim();
            formattedMeaning = `<span class="pos-tag">${extractedPos}</span> ${processedMeaning}`;
        }
        // 如果有词性标签，处理换行和词性标签
        else if (posInfo.length > 0) {
            // 将文本按词性分段
            let segments = [];
            
            // 处理多个词性的情况
            if (posInfo.length > 1) {
                // 检查是否有连续的词性标签（如 v. & aux.）
                // 通过检查两个词性标签之间的文本是否只包含连接符（如 &）来判断
                const consecutivePosGroups = [];
                let currentGroup = [0]; // 从第一个词性开始
                
                for (let i = 0; i < posInfo.length - 1; i++) {
                    const currentPos = posInfo[i];
                    const nextPos = posInfo[i + 1];
                    const textBetween = processedMeaning.substring(
                        currentPos.index + currentPos.length, 
                        nextPos.index
                    ).trim();
                    
                    // 如果两个词性之间只有连接符（如 &），则认为它们是连续的
                    if (textBetween === '&' || textBetween === 'and' || textBetween === '和' || textBetween === '') {
                        // 当前词性和下一个词性是连续的
                        if (!currentGroup.includes(i + 1)) {
                            currentGroup.push(i + 1);
                        }
                    } else {
                        // 当前词性和下一个词性不是连续的，结束当前组
                        if (currentGroup.length > 0) {
                            consecutivePosGroups.push([...currentGroup]);
                            currentGroup = [i + 1];
                        }
                    }
                }
                
                // 处理最后一个组
                if (currentGroup.length > 0) {
                    consecutivePosGroups.push([...currentGroup]);
                }
                
                // 根据连续词性组处理文本
                for (let group of consecutivePosGroups) {
                    // 获取组中最后一个词性的索引
                    const lastPosIndex = group[group.length - 1];
                    const lastPos = posInfo[lastPosIndex];
                    
                    // 计算组的结束索引
                    let endIndex = lastPosIndex < posInfo.length - 1 ? 
                        posInfo[lastPosIndex + 1].index : processedMeaning.length;
                    
                    // 提取该组词性后面的文本
                    let text = processedMeaning.substring(lastPos.index + lastPos.length, endIndex).trim();
                    
                    // 如果文本以连接符开头，去掉连接符
                    if (text.startsWith('&') || text.startsWith('and') || text.startsWith('和')) {
                        text = text.substring(1).trim();
                    }
                    
                    // 检查文本是否为空，如果为空可能是原始数据中缺少该词性的中文意思
                    // 在这种情况下，尝试查找是否有其他词性的中文意思可以使用
                    if (text.trim() === '') {
                        // 查找其他词性组中是否有非空的中文意思
                        for (let otherGroup of consecutivePosGroups) {
                            if (otherGroup !== group) {
                                const otherLastPosIndex = otherGroup[otherGroup.length - 1];
                                const otherLastPos = posInfo[otherLastPosIndex];
                                const otherEndIndex = otherLastPosIndex < posInfo.length - 1 ? 
                                    posInfo[otherLastPosIndex + 1].index : processedMeaning.length;
                                const otherText = processedMeaning.substring(otherLastPos.index + otherLastPos.length, otherEndIndex).trim();
                                
                                if (otherText && !otherText.startsWith('&') && !otherText.startsWith('and') && !otherText.startsWith('和')) {
                                    text = otherText;
                                    break;
                                }
                            }
                        }
                    }
                    
                    // 构建该组的显示文本
                    if (group.length === 1) {
                        // 单个词性
                        segments.push(posInfo[group[0]].pos + ' ' + text);
                    } else {
                        // 连续词性，不添加换行
                        const groupPosText = group.map(idx => posInfo[idx].pos).join(' & ');
                        segments.push(groupPosText + ' ' + text);
                    }
                }
            } 
            // 处理只有一个词性的情况
            else {
                const pos = posInfo[0];
                let text = processedMeaning.substring(pos.index + pos.length).trim();
                segments.push(pos.pos + ' ' + text);
            }
            
            // 用<br>连接所有段落
            formattedMeaning = segments.join('<br>');
        }
        
        // 恢复方括号中的内容，不再使用<small>标签包裹
        for (let i = 0; i < bracketContents.length; i++) {
            // 直接恢复方括号内容，不添加任何标签
            formattedMeaning = formattedMeaning.replace(`__BRACKET_${i}__`, bracketContents[i]);
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

// 注意：formatPOSAndMeaning 函数已在上面定义并添加到全局作用域

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