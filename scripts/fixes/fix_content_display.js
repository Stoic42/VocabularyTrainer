/**
 * 修复content等单词显示问题的脚本
 * 该脚本将处理meaning_cn字段中混入的例句、词根记忆等信息，将它们分离到对应的字段中
 */

// 清理meaning_cn字段的函数
function cleanMeaningCN(meaningCN) {
    if (!meaningCN) return '';
    
    let cleanedMeaning = meaningCN;
    
    // 移除例句（通常在"//"之后）
    const exampleMatch = cleanedMeaning.match(/(.*?)(?:\/\/.*)/);
    if (exampleMatch) {
        cleanedMeaning = exampleMatch[1].trim();
    }
    
    // 移除词根记忆（通常在"词根记忆："之后）
    const mnemonicMatch = cleanedMeaning.match(/(.*?)(?:词根记忆：.*)/);
    if (mnemonicMatch) {
        cleanedMeaning = mnemonicMatch[1].trim();
    }
    
    // 移除搭配用法（通常在数字编号之后，如"1．be content with..."）
    const collocationMatch = cleanedMeaning.match(/(.*?)(?:\d+[．.].*)/);
    if (collocationMatch) {
        cleanedMeaning = collocationMatch[1].trim();
    }
    
    // 移除其他可能的额外信息
    // 移除以"；"开头的额外信息
    cleanedMeaning = cleanedMeaning.replace(/；[^；]*$/, '');
    
    return cleanedMeaning.trim();
}

// 提取例句的函数
function extractExamples(meaningCN) {
    if (!meaningCN) return { example_en: '', example_cn: '' };
    
    const examples = { example_en: '', example_cn: '' };
    
    // 提取"//"之后的例句
    const exampleMatch = meaningCN.match(/\/\/(.*?)(?=词根记忆：|$)/);
    if (exampleMatch) {
        const exampleText = exampleMatch[1].trim();
        
        // 分离英文和中文例句
        const parts = exampleText.split('。');
        if (parts.length >= 2) {
            examples.example_en = parts[0].trim();
            examples.example_cn = parts[1].trim();
        } else {
            // 如果没有中文部分，整个作为英文例句
            examples.example_en = exampleText;
        }
    }
    
    return examples;
}

// 提取词根记忆的函数
function extractMnemonic(meaningCN) {
    if (!meaningCN) return '';
    
    const mnemonicMatch = meaningCN.match(/词根记忆：(.*?)(?=\d+[．.]|$)/);
    if (mnemonicMatch) {
        return mnemonicMatch[1].trim();
    }
    
    return '';
}

// 提取搭配用法的函数
function extractCollocation(meaningCN) {
    if (!meaningCN) return '';
    
    const collocationMatch = meaningCN.match(/(\d+[．.].*)/);
    if (collocationMatch) {
        return collocationMatch[1].trim();
    }
    
    return '';
}

// 修复displayQuestion函数
function fixDisplayQuestion() {
    // 保存原始的displayQuestion函数
    const originalDisplayQuestion = window.displayQuestion;
    
    if (originalDisplayQuestion) {
        window.displayQuestion = function() {
            const q = questions[currentQuestionIndex];
            const studyMode = document.getElementById('study-mode').value;
            
            // 清理meaning_cn字段
            const cleanedMeaningCN = cleanMeaningCN(q.meaning_cn);
            
            // 提取额外信息
            const examples = extractExamples(q.meaning_cn);
            const mnemonic = extractMnemonic(q.meaning_cn);
            const collocation = extractCollocation(q.meaning_cn);
            
            // 使用 formatPOSAndMeaning 函数处理词性和清理后的意思
            const { extractedPos, formattedMeaning } = formatPOSAndMeaning(q.pos, cleanedMeaningCN);
            
            // 显示格式化后的中文释义，包含词性信息
            questionMeaningEl.innerHTML = formattedMeaning || ''; // 使用 innerHTML 以支持 <br> 标签
            questionIpaEl.textContent = q.ipa ? `/${q.ipa}/` : ''; // 音标
            questionMeaningEnEl.textContent = q.meaning_en || ''; // 英文释义
            
            // 使用提取的例句，如果没有提取到则使用原始字段
            questionExampleEnEl.textContent = examples.example_en || q.example_en || ''; // 例句英文
            questionExampleCnEl.textContent = examples.example_cn || q.example_cn || ''; // 例句中文

            // 错词复习模式：准备错误统计信息（但不立即显示）
            let errorInfo = null;
            if (studyMode === 'error_review' && q.error_count) {
                errorInfo = document.createElement('div');
                errorInfo.className = 'error-info';
                errorInfo.style.cssText = `
                    background: #fffbe6;
                    border-left: 3px solid #ffeaa7;
                    border-radius: 0 6px 6px 0;
                    padding: 6px 12px;
                    margin: 8px 0 0 0;
                    color: #856404;
                    font-size: 0.85em;
                    line-height: 1.5;
                    font-weight: normal;
                    box-shadow: none;
                `;
                errorInfo.innerHTML = `
                    <span style="font-size:0.95em;">📊 错词统计：</span>
                    已错误 <strong>${q.error_count}</strong> 次
                    ${q.last_error_date ? `，最近错误：${q.last_error_date}` : ''}
                    ${q.book_name && q.list_name ? `，来自：${q.book_name} - ${q.list_name}` : q.list_name ? `，来自：${q.list_name}` : ''}
                `;
            }
            
            // 移除之前的错误信息（如果有）
            const existingErrorInfo = document.querySelector('.error-info');
            if (existingErrorInfo) existingErrorInfo.remove();

            // 填充更多详细信息，优先使用提取的信息
            questionDerivativesEl.textContent = q.derivatives ? `派生词: ${q.derivatives}` : '';
            questionRootEtymologyEl.textContent = q.root_etymology ? `词根词源: ${q.root_etymology}` : '';
            questionMnemonicEl.textContent = mnemonic ? `联想记忆: ${mnemonic}` : (q.mnemonic ? `联想记忆: ${q.mnemonic}` : '');
            questionComparisonEl.textContent = q.comparison ? `词义辨析: ${q.comparison}` : '';
            questionCollocationEl.textContent = collocation ? `搭配用法: ${collocation}` : (q.collocation ? `搭配用法: ${q.collocation}` : '');
            questionExamSentenceEl.textContent = q.exam_sentence ? `真题例句: ${q.exam_sentence}` : '';
            questionExamYearSourceEl.textContent = q.exam_year_source ? `真题出处: ${q.exam_year_source}` : '';
            questionExamOptionsEl.textContent = q.exam_options ? `选项: ${q.exam_options}` : '';
            questionExamExplanationEl.textContent = q.exam_explanation ? `解析: ${q.exam_explanation}` : '';
            questionTipsEl.textContent = q.tips ? `提示: ${q.tips}` : '';
            
            // 如果有错词统计信息，添加到详情容器的最前面
            if (errorInfo) {
                wordDetailsContainer.insertBefore(errorInfo, wordDetailsContainer.firstChild);
            }

            // 根据学习模式决定是否默认展开详情
            if (studyMode === 'learning' || studyMode === 'error_review') {
                // 学习模式和错词复习模式下默认展开详情
                wordDetailsContainer.style.display = 'block';
                toggleDetailsBtn.textContent = '隐藏更多详情';
            } else {
                // 其他模式下默认隐藏详情
                wordDetailsContainer.style.display = 'none';
                toggleDetailsBtn.textContent = '显示更多详情';
            }
            
            currentQNumEl.textContent = currentQuestionIndex + 1;

            // 根据学习模式和音频路径决定是否显示音频按钮
            const showAudio = studyMode === 'standard' || studyMode === 'error_review';
            
            // 显示TTS按钮，无论是否有本地音频
            const ttsBtn = document.createElement('button');
            ttsBtn.className = 'audio-btn';
            ttsBtn.innerHTML = '<i class="fas fa-volume-up"></i> TTS';
            ttsBtn.onclick = () => playTTS(q.spelling);
            
            // 清除之前的TTS按钮
            const oldTtsBtn = document.querySelector('.audio-btn.tts-btn');
            if (oldTtsBtn) oldTtsBtn.remove();
            
            // 添加TTS按钮样式
            ttsBtn.classList.add('tts-btn');
            ttsBtn.style.backgroundColor = '#9b59b6';
            ttsBtn.style.marginLeft = '5px';
            
            // 显示音频按钮
            ukBtn.style.display = showAudio && q.audio_path_uk ? 'inline-block' : 'none';
            usBtn.style.display = showAudio && q.audio_path_us ? 'inline-block' : 'none';
            
            if (showAudio) {
                if (q.audio_path_uk) ukBtn.onclick = () => playAudio(q.audio_path_uk, q.spelling);
                if (q.audio_path_us) usBtn.onclick = () => playAudio(q.audio_path_us, q.spelling);
                
                // 添加TTS按钮到音频按钮区域
                const audioButtonsContainer = ukBtn.parentElement;
                audioButtonsContainer.appendChild(ttsBtn);
            }

            nextBtn.textContent = (currentQuestionIndex === questions.length - 1) ? '完成并提交' : '下一题';
            
            // 新题显示后，添加延时控制
            inputEnabled = false; // 禁用"下一个"操作
            nextBtn.disabled = true;
            
            // 0.6秒后启用"下一个"操作
            setTimeout(() => {
                inputEnabled = true;
                nextBtn.disabled = false;
                answerInput.focus();
            }, 600);
            
            // 如果启用了自动播放且支持音频，自动播放音频
            if (autoPlayEnabled && showAudio) {
                setTimeout(() => autoPlayAudios(), 500); // 延迟500ms后播放，给页面渲染一些时间
            }
        };
    }
}

// 修复错误历史页面的显示
function fixErrorHistoryDisplay() {
    // 如果有错误历史页面的相关函数，也需要修复
    if (typeof window.renderErrorHistory === 'function') {
        const originalRenderErrorHistory = window.renderErrorHistory;
        window.renderErrorHistory = function(data) {
            // 处理数据，清理meaning_cn字段
            if (data && data.errors) {
                data.errors.forEach(error => {
                    if (error.meaning_cn) {
                        error.meaning_cn = cleanMeaningCN(error.meaning_cn);
                    }
                });
            }
            
            // 调用原始函数
            return originalRenderErrorHistory(data);
        };
    }
}

// 初始化修复
function initContentDisplayFix() {
    console.log('正在初始化content显示修复...');
    
    // 等待页面加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            fixDisplayQuestion();
            fixErrorHistoryDisplay();
            console.log('content显示修复完成');
        });
    } else {
        fixDisplayQuestion();
        fixErrorHistoryDisplay();
        console.log('content显示修复完成');
    }
}

// 自动初始化
initContentDisplayFix(); 