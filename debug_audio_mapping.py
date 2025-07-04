import os

def debug_audio_mapping():
    """调试音频文件分类逻辑"""
    print("🔍 调试音频文件分类")
    print("=" * 60)
    
    media_dir = "wordlists/senior_high/media"
    
    # 获取所有音频文件
    all_files = []
    for file in os.listdir(media_dir):
        if file.endswith('.mp3'):
            all_files.append(file)
    
    print(f"📊 总音频文件数: {len(all_files)}")
    
    # 分类音频文件
    uk_files = []
    us_files = []
    other_files = []
    
    for file in all_files:
        if file.startswith('cambridge-') and not file.startswith('cambridgeee-'):
            uk_files.append(file)
        elif file.startswith('cambridgeee-'):
            us_files.append(file)
        else:
            other_files.append(file)
    
    print(f"🇬🇧 英音文件 (cambridge-): {len(uk_files)} 个")
    print(f"🇺🇸 美音文件 (cambridgeee-): {len(us_files)} 个")
    print(f"❓ 其他文件: {len(other_files)} 个")
    
    # 显示一些示例
    if uk_files:
        print(f"\n🇬🇧 英音示例 (前5个):")
        for i, file in enumerate(uk_files[:5]):
            print(f"  {i+1}. {file}")
    
    if us_files:
        print(f"\n🇺🇸 美音示例 (前5个):")
        for i, file in enumerate(us_files[:5]):
            print(f"  {i+1}. {file}")
    
    if other_files:
        print(f"\n❓ 其他文件示例 (前5个):")
        for i, file in enumerate(other_files[:5]):
            print(f"  {i+1}. {file}")

if __name__ == "__main__":
    debug_audio_mapping() 