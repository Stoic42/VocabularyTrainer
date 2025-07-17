import os
from gtts import gTTS
import hashlib

# TTS音频缓存目录
TTS_CACHE_DIR = 'd:\\Projects\\VocabularyTrainer\\wordlists\\tts_cache'
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

# 测试单词列表
test_words = ['thief', 'woman', 'dare', 'horoscope']

# 文本预处理函数
def preprocess_text_for_tts(text):
    """预处理文本以优化TTS效果"""
    # 处理特殊情况
    text = text.replace('a/an', 'a or an')
    text = text.replace('/', ' or ')
    # 可以添加更多替换规则
    return text

# 生成TTS音频
def generate_tts(word):
    # 文本预处理
    processed_word = preprocess_text_for_tts(word)
    
    # 生成文件名（使用哈希避免文件名问题）
    filename = hashlib.md5(processed_word.encode()).hexdigest() + '.mp3'
    filepath = os.path.join(TTS_CACHE_DIR, filename)
    
    print(f"生成TTS音频: {word} -> {filepath}")
    
    # 生成TTS音频
    tts = gTTS(text=processed_word, lang='en', slow=False)
    tts.save(filepath)
    
    return filepath

# 主函数
def main():
    print("===== 测试gTTS对特定单词的发音 =====")
    
    for word in test_words:
        try:
            filepath = generate_tts(word)
            print(f"成功生成TTS音频: {word} -> {filepath}")
        except Exception as e:
            print(f"生成TTS音频失败: {word}, 错误: {str(e)}")
    
    print("\n===== 测试完成 =====")
    print(f"请手动检查生成的音频文件是否正确发音。")
    print(f"音频文件保存在: {TTS_CACHE_DIR}")

if __name__ == "__main__":
    main()