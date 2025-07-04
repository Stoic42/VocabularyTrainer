import re

def check_anki_audio_mapping():
    """检查Anki文件中的音频映射情况"""
    anki_file = "wordlists/senior_high/高中 乱序 绿宝书.txt"
    
    print("🔍 检查Anki文件中的音频映射")
    print("=" * 60)
    
    with open(anki_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配单词和音频文件
    pattern = r'^([a-zA-Z\-\']+)\t.*?\t\[sound:([^\]]+\.mp3)\]\t([^\t]+)'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    print(f"📊 找到 {len(matches)} 个单词-音频映射")
    
    # 检查是否有重复的音频文件
    audio_files = {}
    for match in matches:
        word = match[0].strip().lower()
        audio_file = match[1].strip()
        pronunciation = match[2].strip()
        
        if audio_file not in audio_files:
            audio_files[audio_file] = []
        audio_files[audio_file].append(word)
    
    # 显示重复的音频文件
    duplicates = {file: words for file, words in audio_files.items() if len(words) > 1}
    
    if duplicates:
        print(f"\n⚠️  发现 {len(duplicates)} 个音频文件被多个单词使用:")
        for audio_file, words in list(duplicates.items())[:10]:
            print(f"  {audio_file}: {', '.join(words[:5])}{'...' if len(words) > 5 else ''}")
        if len(duplicates) > 10:
            print(f"  ... 还有 {len(duplicates) - 10} 个重复文件")
    else:
        print("\n✅ 没有发现重复的音频文件")
    
    # 显示一些示例映射
    print(f"\n📝 示例映射 (前10个):")
    for i, match in enumerate(matches[:10]):
        word = match[0].strip().lower()
        audio_file = match[1].strip()
        pronunciation = match[2].strip()
        print(f"  {i+1}. {word} -> {audio_file} ({pronunciation})")
    
    # 检查音频文件命名模式
    print(f"\n🔍 音频文件命名分析:")
    uk_files = [f for f in audio_files.keys() if 'cambridge-' in f and not 'cambridgeee-' in f]
    us_files = [f for f in audio_files.keys() if 'cambridgeee-' in f]
    
    print(f"  英音文件 (cambridge-): {len(uk_files)} 个")
    print(f"  美音文件 (cambridgeee-): {len(us_files)} 个")
    
    if uk_files:
        print(f"  英音示例: {uk_files[0]}")
    if us_files:
        print(f"  美音示例: {us_files[0]}")

if __name__ == "__main__":
    check_anki_audio_mapping() 