/**
 * 修复单词"mess"被错误显示为"mass"的问题
 * 这个脚本会检查错误历史页面中的错误答案，确保正确显示
 */

// 在页面加载完成后执行修复
document.addEventListener('DOMContentLoaded', function() {
    // 检测当前页面是否是错误历史页面
    const isErrorHistoryPage = window.location.pathname.includes('error-history');
    
    if (isErrorHistoryPage) {
        fixErrorHistoryPage();
    }
});

/**
 * 格式化词性，将分号或空格分隔的词性转换为换行显示
 * @param {string} pos 词性字符串
 * @returns {string} 格式化后的HTML
 */
function formatPOS(pos) {
    if (!pos) return '';
    return pos.replace(/;|\s+/g, '<br>');
}

/**
 * 格式化多义词的中文意思，根据词性分割并格式化
 * @param {string} meaning 中文意思
 * @param {string} pos 词性
 * @returns {string} 格式化后的HTML
 */
function formatMultiMeanings(meaning, pos) {
    if (!meaning) return '';
    if (!pos) return meaning;
    
    // 检查meaning_cn中是否已经包含词性标记
    const posPattern = /([a-z]+\.)/gi;
    const posMatches = meaning.match(posPattern);
    
    if (posMatches && posMatches.length > 0) {
        // 如果中文意思中已经包含词性标记，按词性分割并格式化显示
        let formattedMeaning = meaning;
        
        // 为每个词性添加样式，并在词性前添加换行（除了第一个）
        posMatches.forEach((posTag, index) => {
            const regex = new RegExp(`(${posTag})`, 'g');
            if (index === 0) {
                // 第一个词性，只添加样式
                formattedMeaning = formattedMeaning.replace(regex, '<span class="pos-tag">$1</span>');
            } else {
                // 后续词性，添加换行和样式
                formattedMeaning = formattedMeaning.replace(regex, '<br><span class="pos-tag">$1</span>');
            }
        });
        
        return formattedMeaning;
    } else {
        // 如果中文意思中没有词性标记，在开头添加词性
        const extractedPos = pos.trim();
        return `<span class="pos-tag">${extractedPos}</span> ${meaning}`;
    }
}

// 修复错误历史页面
function fixErrorHistoryPage() {
    console.log('正在修复错误历史页面...');
    
    // 添加CSS样式
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .pos-tag {
            display: inline-block;
            margin-right: 4px;
            padding: 1px 6px;
            background-color: var(--primary-color-light, #e3f2fd);
            color: var(--primary-color-dark, #1976d2);
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }
        
        .wrong-answer {
            display: inline-block;
            margin: 2px;
            padding: 2px 8px;
            background-color: var(--error-color-light, #ffebee);
            color: var(--error-color, #c0392b);
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        /* 确保错误答案在鼠标悬停时显示日期 */
        .wrong-answer:hover {
            position: relative;
        }
        
        .wrong-answer:hover::after {
            content: attr(title);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            white-space: nowrap;
            z-index: 10;
        }
        
        /* 高亮显示拼写为mess但错误答案为mass的情况 */
        .mess-mass-highlight {
            position: relative;
        }
        
        .mess-mass-highlight::after {
            content: "(注意: 这是学生的实际错误答案)";
            position: absolute;
            top: 100%;
            left: 0;
            font-size: 0.8em;
            color: #e67e22;
            white-space: nowrap;
        }
    `;
    document.head.appendChild(styleElement);
    
    // 修复最近错误的显示
    const originalDisplayRecentErrors = window.displayRecentErrors;
    if (originalDisplayRecentErrors) {
        window.displayRecentErrors = function(errors) {
            // 处理错误数据
            if (errors && errors.length > 0) {
                errors.forEach(error => {
                    // 检查拼写是否为"mess"
                    if (error.spelling && error.spelling.toLowerCase() === 'mess') {
                        // 检查学生答案是否为"mass"
                        if (error.student_answer && error.student_answer.toLowerCase() === 'mass') {
                            console.log('检测到mess/mass错误对');
                            // 添加标记，但不修改原始答案
                            error.highlightAnswer = true;
                        }
                    }
                    
                    // 格式化中文意思
                    if (error.meaning_cn && error.pos) {
                        error.formatted_meaning = formatMultiMeanings(error.meaning_cn, error.pos);
                    }
                });
            }
            
            // 调用原始函数
            const result = originalDisplayRecentErrors(errors);
            
            // 在渲染完成后添加高亮
            setTimeout(() => {
                const errorRows = document.querySelectorAll('#recentErrorsTable tbody tr');
                errorRows.forEach((row, index) => {
                    if (errors[index] && errors[index].highlightAnswer) {
                        const answerCell = row.querySelector('td:nth-child(6)');
                        if (answerCell) {
                            answerCell.classList.add('mess-mass-highlight');
                        }
                    }
                });
            }, 100);
            
            return result;
        };
    }
    
    // 修复单词错误历史的显示
    const originalRenderWordHistory = window.renderWordHistory;
    if (originalRenderWordHistory) {
        window.renderWordHistory = function(wordHistory) {
            // 处理单词历史数据
            if (wordHistory && wordHistory.length > 0) {
                wordHistory.forEach(word => {
                    // 检查拼写是否为"mess"
                    if (word.spelling && word.spelling.toLowerCase() === 'mess') {
                        // 格式化中文意思
                        if (word.meaning_cn && word.pos) {
                            word.formatted_meaning = formatMultiMeanings(word.meaning_cn, word.pos);
                        }
                        
                        // 处理错误答案
                        if (word.wrong_answers && word.error_dates) {
                            const wrongAnswers = word.wrong_answers.split(', ');
                            const errorDates = word.error_dates.split(', ');
                            
                            // 创建带有日期的错误答案HTML
                            let wrongAnswersHtml = '';
                            wrongAnswers.forEach((answer, i) => {
                                const date = i < errorDates.length ? errorDates[i] : '';
                                const highlightClass = (answer.toLowerCase() === 'mass') ? 'mess-mass-highlight' : '';
                                wrongAnswersHtml += `<span class="wrong-answer ${highlightClass}" title="${date}">${answer}</span> `;
                            });
                            
                            word.wrongAnswersHtml = wrongAnswersHtml;
                        }
                    }
                });
            }
            
            // 调用原始函数
            return originalRenderWordHistory(wordHistory);
        };
    }
    
    // 修改renderErrorHistory函数以使用我们的格式化函数
    const originalRenderErrorHistory = window.renderErrorHistory;
    if (originalRenderErrorHistory) {
        window.renderErrorHistory = function(data) {
            // 处理数据
            if (data) {
                // 处理最近错误
                if (data.errors && data.errors.length > 0) {
                    data.errors.forEach(error => {
                        // 格式化词性和中文意思
                        if (error.pos) {
                            error.formatted_pos = formatPOS(error.pos);
                        }
                        if (error.meaning_cn && error.pos) {
                            error.formatted_meaning = formatMultiMeanings(error.meaning_cn, error.pos);
                        }
                    });
                }
                
                // 处理单词历史
                if (data.word_history && data.word_history.length > 0) {
                    data.word_history.forEach(word => {
                        // 格式化词性和中文意思
                        if (word.pos) {
                            word.formatted_pos = formatPOS(word.pos);
                        }
                        if (word.meaning_cn && word.pos) {
                            word.formatted_meaning = formatMultiMeanings(word.meaning_cn, word.pos);
                        }
                    });
                }
            }
            
            // 调用原始函数
            return originalRenderErrorHistory(data);
        };
    }
    
    console.log('错误历史页面修复完成');
}