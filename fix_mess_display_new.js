/**
 * 修复多词性多义项单词显示问题的脚本
 * 该脚本将重新设计错误历史和出题界面中词性和义项的显示逻辑
 */

// 格式化词性和意思的函数
function extractPOSAndMeaning(pos, meaning) {
    if (!pos && !meaning) {
        return { extractedPos: 'N/A', formattedMeaning: 'N/A' };
    }
    
    // 处理中文意思中的词性格式，如 "n. / v. 回答，答复，以…作答"
    // 支持多种格式："n. / v."、"n./v."、"n. v."、"n. & v."等
    if (meaning) {
        // 匹配开头的词性部分，支持多种分隔符
        // 更健壮的正则表达式，可以匹配各种格式的词性组合
        // 处理 "n. / v."、"n./v."、"n. v."、"n. & v."、"n. /<br>v." 等格式
        const posPartMatch = meaning.match(/^([a-z]+\.\s*(?:(?:[\/\s&]+|<br>)\s*[a-z]+\.)+|[a-z]+\.\s*(?:[\/\s&]+|<br>)\s*[a-z]+\.\s*) (.+)$/i);
        if (posPartMatch) {
            const posPart = posPartMatch[1];
            const meaningPart = posPartMatch[2];
            // 处理 posPart 中可能存在的 <br> 标签
            // 将 <br> 替换为空格，以便在 extractedPos 中正确显示
            const cleanPosPart = posPart.replace(/<br>/g, ' ');
            
            // 保持词性和意思在同一行
            // 在 formattedMeaning 中保留原始格式，包括可能的 <br> 标签
            return { extractedPos: cleanPosPart, formattedMeaning: `${posPart} ${meaningPart}` };
        }
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
        
        // 如果有词性标签，处理换行和词性标签
        if (posInfo.length > 0) {
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
    
    // 检查是否已经存在错误历史表格
    const recentErrorsTable = document.getElementById('recent-errors-table');
    if (!recentErrorsTable) {
        console.log('未找到错误历史表格，跳过修复');
        return;
    }
    
    // 查找所有表格行
    const rows = recentErrorsTable.querySelectorAll('tr');
    if (!rows || rows.length === 0) {
        console.log('错误历史表格为空，跳过修复');
        return;
    }
    
    // 遍历每一行，修复词性和意思的显示
    rows.forEach(row => {
        // 跳过表头行和无数据行
        if (row.querySelector('th') || row.querySelector('.no-data')) {
            return;
        }
        
        // 获取词性和意思单元格
        const cells = row.querySelectorAll('td');
        if (cells.length < 3) {
            return;
        }
        
        // 假设第2列是词性，第3列是意思
        const posCell = cells[1];
        const meaningCell = cells[2];
        
        // 获取原始内容
        const originalPos = posCell.textContent.trim();
        const originalMeaning = meaningCell.innerHTML.trim();
        
        // 重新格式化
        const result = extractPOSAndMeaning(originalPos, originalMeaning);
        
        // 更新单元格内容
        posCell.textContent = result.extractedPos;
        meaningCell.innerHTML = result.formattedMeaning;
    });
    
    console.log('错误历史页面修复完成');
}

// 修复考核页面
function fixAssessmentPage() {
    console.log('正在修复考核页面...');
    
    // 检查是否存在问题意思元素
    const questionMeaningEl = document.getElementById('question-meaning');
    if (!questionMeaningEl) {
        console.log('未找到问题意思元素，跳过修复');
        return;
    }
    
    // 监听 displayQuestion 函数调用
    // 由于我们不能直接修改 displayQuestion 函数，我们可以通过 MutationObserver 监听 DOM 变化
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                // 当问题意思元素内容变化时，检查并修复词性显示
                const content = questionMeaningEl.innerHTML;
                if (content && content.includes('<br>')) {
                    // 如果内容中包含 <br> 标签，可能需要修复
                    // 尝试提取词性和意思
                    const result = extractPOSAndMeaning('', content);
                    if (result.formattedMeaning !== content) {
                        // 如果格式化后的内容与原内容不同，更新内容
                        questionMeaningEl.innerHTML = result.formattedMeaning;
                    }
                }
            }
        });
    });
    
    // 配置 observer
    const config = { childList: true, characterData: true, subtree: true };
    
    // 开始观察
    observer.observe(questionMeaningEl, config);
    
    console.log('考核页面修复完成');
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