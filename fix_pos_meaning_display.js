/**
 * 修复词性和意思显示问题的脚本
 * 该脚本将formatMultiMeanings和formatPOS函数添加到LumiCamp_for_Alan的错词和考核界面中
 */

// 格式化词性函数
function formatPOS(pos) {
    if (!pos) return '-';
    
    // 将词性按照分号或空格分割，并用<br>连接
    return pos.replace(/([a-z]+\.)(\s|;)/gi, '$1<br>');
}

// 格式化多义词的显示函数
function formatMultiMeanings(meaning, pos) {
    if (!pos || !meaning) return meaning || '-';
    
    // 分割词性和意思
    const posItems = pos.split(/\s*[;\s]\s*/).filter(p => p.trim());
    
    // 如果只有一个词性或没有词性，直接返回原意思
    if (posItems.length <= 1) return meaning;
    
    // 尝试将意思按照词性分割
    const meaningParts = meaning.split(/\s*[;\s]\s*/).filter(m => m.trim());
    
    // 如果意思部分少于词性部分，可能格式不匹配，返回原意思
    if (meaningParts.length < posItems.length) return meaning;
    
    // 构建格式化后的意思
    let formattedMeaning = '';
    let meaningIndex = 0;
    
    for (let i = 0; i < posItems.length; i++) {
        const posItem = posItems[i].trim();
        // 为每个词性找到对应的意思
        if (meaningIndex < meaningParts.length) {
            formattedMeaning += `<div><span class="pos-tag">${posItem}</span> ${meaningParts[meaningIndex]}</div>`;
            meaningIndex++;
        }
    }
    
    // 如果还有剩余的意思，添加到最后
    while (meaningIndex < meaningParts.length) {
        formattedMeaning += `<div>${meaningParts[meaningIndex]}</div>`;
        meaningIndex++;
    }
    
    return formattedMeaning || meaning;
}

// 修复LumiCamp_for_Alan的错词界面
function fixErrorHistoryPage() {
    // 1. 添加CSS样式
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
    `;
    document.head.appendChild(styleElement);
    
    // 2. 修改错词卡片的显示逻辑
    const originalDisplayRecentErrors = window.displayRecentErrors;
    if (originalDisplayRecentErrors) {
        window.displayRecentErrors = function(data) {
            if (!data || !data.recent_errors || data.recent_errors.length === 0) {
                recentErrorsContent.innerHTML = '<div class="no-data">暂无最近错误记录</div>';
                return;
            }
            
            let html = '';
            data.recent_errors.forEach(error => {
                html += `
                <div class="error-card">
                    <h3>
                        ${error.spelling}
                        <span class="error-count">${error.error_count}次</span>
                    </h3>
                    <p class="meaning">${formatMultiMeanings(error.meaning_cn, error.pos) || '-'}</p>
                    <p>${error.ipa ? `/${error.ipa}/` : ''} ${error.meaning_en || ''}</p>
                    ${error.example_en ? `<p class="example">${error.example_en}</p>` : ''}
                    ${error.example_cn ? `<p class="example">${error.example_cn}</p>` : ''}
                    <p style="margin-top: 10px; color: #999;">最近错误: ${formatDate(error.last_error_time)}</p>
                </div>
                `;
            });
            
            recentErrorsContent.innerHTML = html;
        };
    }
    
    // 3. 修改单词历史表格的显示逻辑
    const originalDisplayWordHistory = window.displayWordHistory;
    if (originalDisplayWordHistory) {
        window.displayWordHistory = function(data) {
            wordHistoryLoading.style.display = 'none';
            wordHistoryContent.style.display = 'block';
            
            if (!data || !data.word_history || data.word_history.length === 0) {
                wordHistoryTable.innerHTML = '<tr><td colspan="4" class="no-data">暂无错误记录</td></tr>';
                return;
            }
            
            let html = '';
            data.word_history.forEach(word => {
                html += `
                <tr>
                    <td>${word.spelling}</td>
                    <td><span class="error-count">${word.error_count}</span></td>
                    <td>${formatDate(word.last_error_time)}</td>
                    <td>${formatMultiMeanings(word.meaning_cn, word.pos) || '-'}</td>
                </tr>
                `;
            });
            
            wordHistoryTable.innerHTML = html;
        };
    }
}

// 修复LumiCamp_for_Alan的考核界面
function fixAssessmentPage() {
    // 1. 修改显示问题的函数
    const originalDisplayQuestion = window.displayQuestion;
    if (originalDisplayQuestion) {
        window.displayQuestion = function() {
            const q = questions[currentQuestionIndex];
            questionMeaningEl.innerHTML = formatMultiMeanings(q.meaning_cn, q.pos) || '-'; // 使用innerHTML而不是textContent
            questionIpaEl.textContent = q.ipa ? `/${q.ipa}/` : ''; // 音标
            questionMeaningEnEl.textContent = q.meaning_en || ''; // 英文释义
            questionExampleEnEl.textContent = q.example_en || ''; // 例句英文
            questionExampleCnEl.textContent = q.example_cn || ''; // 例句中文

            // 填充更多详细信息
            questionDerivativesEl.textContent = q.derivatives ? `派生词: ${q.derivatives}` : '';
            questionRootEtymologyEl.textContent = q.root_etymology ? `词根词源: ${q.root_etymology}` : '';
            questionMnemonicEl.textContent = q.mnemonic ? `联想记忆: ${q.mnemonic}` : '';
            questionComparisonEl.textContent = q.comparison ? `词义辨析: ${q.comparison}` : '';
            questionCollocationEl.textContent = q.collocation ? `搭配用法: ${q.collocation}` : '';
            questionExamSentenceEl.textContent = q.exam_sentence ? `真题例句: ${q.exam_sentence}` : '';
            questionExamYearSourceEl.textContent = q.exam_year_source ? `真题出处: ${q.exam_year_source}` : '';
            questionExamOptionsEl.textContent = q.exam_options ? `选项: ${q.exam_options}` : '';
            questionExamExplanationEl.textContent = q.exam_explanation ? `解析: ${q.exam_explanation}` : '';
            questionTipsEl.textContent = q.tips ? `提示: ${q.tips}` : '';

            // 重置详情显示状态
            wordDetailsContainer.style.display = 'none';
            toggleDetailsBtn.textContent = '显示更多详情';
            currentQNumEl.textContent = currentQuestionIndex + 1;

            ukBtn.style.display = q.audio_path_uk ? 'inline-block' : 'none';
            usBtn.style.display = q.audio_path_us ? 'inline-block' : 'none';
            
            if (q.audio_path_uk) ukBtn.onclick = () => playAudio(q.audio_path_uk, q.spelling);
            if (q.audio_path_us) usBtn.onclick = () => playAudio(q.audio_path_us, q.spelling);

            nextBtn.textContent = (currentQuestionIndex === questions.length - 1) ? '完成并提交' : '下一题';
            answerInput.focus();
            
            // 如果启用了自动播放，自动播放音频
            if (autoPlayEnabled) {
                setTimeout(() => autoPlayAudios(), 500); // 延迟500ms后播放，给页面渲染一些时间
            }
        };
    }
    
    // 2. 修改显示结果的函数
    const originalDisplayResults = window.displayResults;
    if (originalDisplayResults) {
        window.displayResults = function(results) {
            resultsArea.style.display = 'block';
            document.getElementById('error-count').textContent = results.error_count;
            const errorListEl = document.getElementById('error-list');
            errorListEl.innerHTML = '';

            if (results.error_details && results.error_details.length > 0) {
                results.error_details.forEach(err => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <strong>正确:</strong> ${err.correct_spelling} / <strong>你的答案:</strong> <span style="color: #c0392b;">${err.your_answer}</span><br>
                        <strong>词性和意思:</strong> ${formatMultiMeanings(err.meaning_cn, err.pos) || '-'}
                    `;
                    errorListEl.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.innerHTML = '🎉 恭喜你，全部正确！太棒了！';
                li.style.borderLeftColor = '#27ae60';
                li.style.background = '#f0fff4';
                errorListEl.appendChild(li);
            }

            if (!document.getElementById('back-btn')) {
                const backBtn = document.createElement('button');
                backBtn.id = 'back-btn';
                backBtn.textContent = '返回开始界面';
                backBtn.style.marginTop = '20px';
                backBtn.onclick = function() { location.reload(); };
                resultsArea.appendChild(backBtn);
            }
        };
    }
}

// 在页面加载完成后执行修复
document.addEventListener('DOMContentLoaded', function() {
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