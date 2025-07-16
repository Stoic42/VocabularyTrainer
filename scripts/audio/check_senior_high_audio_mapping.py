#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check and match word-audio file mappings for senior high vocabulary
"""

import os
import re
import csv
from pathlib import Path

def extract_audio_files_from_txt(txt_file):
    """Extract audio file references from the Senior_high.txt file"""
    audio_mappings = {}
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Split by tab
            parts = line.split('\t')
            if len(parts) >= 2:
                word = parts[0].strip()
                if word and word != 'Word':
                    # Extract audio file names from the line
                    audio_files = re.findall(r'cambridge-[a-f0-9-]+\.mp3', line)
                    if audio_files:
                        audio_mappings[word] = audio_files
    
    return audio_mappings

def get_available_audio_files(media_dir):
    """Get list of available audio files in the media directory"""
    audio_files = set()
    if os.path.exists(media_dir):
        for file in os.listdir(media_dir):
            if file.endswith('.mp3'):
                audio_files.add(file)
    return audio_files

def get_words_from_csv(csv_file):
    """Extract words from the CSV file"""
    words = []
    word_data = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row.get('Word', '').strip()
            if word and word not in ['Word', '前缀', '后缀', '词根']:
                words.append(word)
                word_data[word] = row
    return words, word_data

def check_audio_mapping():
    """Main function to check audio mapping"""
    txt_file = 'wordlists/senior_high/Senior_high.txt'
    csv_file = 'wordlists/senior_high/senior_high_complete.csv'
    media_dir = 'wordlists/senior_high/media'
    
    print("=== Senior High Audio Mapping Check ===\n")
    
    # Get audio mappings from txt file
    print("1. Extracting audio mappings from Senior_high.txt...")
    txt_audio_mappings = extract_audio_files_from_txt(txt_file)
    print(f"   Found {len(txt_audio_mappings)} words with audio references")
    
    # Get available audio files
    print("\n2. Checking available audio files...")
    available_audio = get_available_audio_files(media_dir)
    print(f"   Found {len(available_audio)} audio files in media directory")
    
    # Get words from CSV
    print("\n3. Extracting words from CSV...")
    csv_words, csv_word_data = get_words_from_csv(csv_file)
    print(f"   Found {len(csv_words)} words in CSV")
    
    # Check for missing audio files
    print("\n4. Checking for missing audio files...")
    missing_audio = set()
    for word, audio_files in txt_audio_mappings.items():
        for audio_file in audio_files:
            if audio_file not in available_audio:
                missing_audio.add(audio_file)
    
    if missing_audio:
        print(f"   Found {len(missing_audio)} missing audio files:")
        for audio in sorted(missing_audio)[:10]:  # Show first 10
            print(f"     - {audio}")
        if len(missing_audio) > 10:
            print(f"     ... and {len(missing_audio) - 10} more")
    else:
        print("   All referenced audio files are available")
    
    # Check for unused audio files
    print("\n5. Checking for unused audio files...")
    used_audio = set()
    for audio_files in txt_audio_mappings.values():
        used_audio.update(audio_files)
    
    unused_audio = available_audio - used_audio
    if unused_audio:
        print(f"   Found {len(unused_audio)} unused audio files:")
        for audio in sorted(unused_audio)[:10]:  # Show first 10
            print(f"     - {audio}")
        if len(unused_audio) > 10:
            print(f"     ... and {len(unused_audio) - 10} more")
    else:
        print("   All audio files are referenced")
    
    # Check for words in CSV but not in txt
    print("\n6. Checking for words in CSV but not in txt...")
    txt_words = set(txt_audio_mappings.keys())
    csv_only_words = set(csv_words) - txt_words
    if csv_only_words:
        print(f"   Found {len(csv_only_words)} words in CSV but not in txt:")
        for word in sorted(csv_only_words):
            print(f"     - {word}")
    else:
        print("   All CSV words are present in txt file")
    
    # Check for words in txt but not in CSV
    print("\n7. Checking for words in txt but not in CSV...")
    txt_only_words = txt_words - set(csv_words)
    if txt_only_words:
        print(f"   Found {len(txt_only_words)} words in txt but not in CSV:")
        for word in sorted(txt_only_words):
            print(f"     - {word}")
    else:
        print("   All txt words are present in CSV")
    
    # Summary
    print("\n=== Summary ===")
    print(f"Total words in CSV: {len(csv_words)}")
    print(f"Total words in txt with audio: {len(txt_audio_mappings)}")
    print(f"Total audio files available: {len(available_audio)}")
    print(f"Missing audio files: {len(missing_audio)}")
    print(f"Unused audio files: {len(unused_audio)}")
    print(f"Words in CSV only: {len(csv_only_words)}")
    print(f"Words in txt only: {len(txt_only_words)}")
    
    # Generate detailed report
    generate_detailed_report(txt_audio_mappings, available_audio, csv_words, csv_word_data, 
                           missing_audio, unused_audio, csv_only_words, txt_only_words)
    
    return {
        'txt_audio_mappings': txt_audio_mappings,
        'available_audio': available_audio,
        'csv_words': csv_words,
        'missing_audio': missing_audio,
        'unused_audio': unused_audio,
        'csv_only_words': csv_only_words,
        'txt_only_words': txt_only_words
    }

def generate_detailed_report(txt_audio_mappings, available_audio, csv_words, csv_word_data, 
                           missing_audio, unused_audio, csv_only_words, txt_only_words):
    """Generate a detailed report file"""
    
    report_file = 'senior_high_audio_mapping_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== Senior High Audio Mapping Detailed Report ===\n\n")
        
        f.write(f"SUMMARY:\n")
        f.write(f"- Total words in CSV: {len(csv_words)}\n")
        f.write(f"- Total words in txt with audio: {len(txt_audio_mappings)}\n")
        f.write(f"- Total audio files available: {len(available_audio)}\n")
        f.write(f"- Missing audio files: {len(missing_audio)}\n")
        f.write(f"- Unused audio files: {len(unused_audio)}\n")
        f.write(f"- Words in CSV only: {len(csv_only_words)}\n")
        f.write(f"- Words in txt only: {len(txt_only_words)}\n\n")
        
        if csv_only_words:
            f.write("WORDS IN CSV BUT NOT IN TXT (need audio mapping):\n")
            f.write("=" * 50 + "\n")
            for word in sorted(csv_only_words):
                if word in csv_word_data:
                    row = csv_word_data[word]
                    meaning = row.get('Meaning (CN)', '')
                    example = row.get('Example', '')
                    f.write(f"Word: {word}\n")
                    f.write(f"Meaning: {meaning}\n")
                    f.write(f"Example: {example}\n")
                    f.write("-" * 30 + "\n")
            f.write("\n")
        
        if txt_only_words:
            f.write("WORDS IN TXT BUT NOT IN CSV:\n")
            f.write("=" * 30 + "\n")
            for word in sorted(txt_only_words):
                f.write(f"- {word}\n")
            f.write("\n")
        
        if missing_audio:
            f.write("MISSING AUDIO FILES:\n")
            f.write("=" * 20 + "\n")
            for audio in sorted(missing_audio):
                f.write(f"- {audio}\n")
            f.write("\n")
        
        if unused_audio:
            f.write("UNUSED AUDIO FILES (first 50):\n")
            f.write("=" * 30 + "\n")
            for audio in sorted(unused_audio)[:50]:
                f.write(f"- {audio}\n")
            if len(unused_audio) > 50:
                f.write(f"... and {len(unused_audio) - 50} more\n")
            f.write("\n")
        
        # Sample of word-audio mappings
        f.write("SAMPLE WORD-AUDIO MAPPINGS:\n")
        f.write("=" * 30 + "\n")
        count = 0
        for word, audio_files in sorted(txt_audio_mappings.items()):
            if count >= 20:  # Show first 20
                break
            f.write(f"{word}: {', '.join(audio_files)}\n")
            count += 1
        f.write("\n")
    
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    check_audio_mapping() 