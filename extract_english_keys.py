#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт извлекает все ключи и их английские переводы из I2Languages.json
в один файл (ключ -> английский текст).
Запуск:  run_extract_english_keys.bat  или  py -u extract_english_keys.py
"""

import json
import os
import sys

# Сразу выводим, что скрипт запустился (без буфера)
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Индекс английского в массиве Languages (см. mLanguages: 0=简体中文, 1=English, 2=日本語, 3=繁体中文)
ENGLISH_INDEX = 1

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "I2Languages.json")
    output_path = os.path.join(script_dir, "english_keys.json")

    if not os.path.exists(input_path):
        print(f"Файл не найден: {input_path}")
        return 1

    print("Загрузка I2Languages.json...", flush=True)
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    terms = data.get("m_Structure", {}).get("mSource", {}).get("mTerms", [])
    if not terms:
        print("Не найдено m_Structure.mSource.mTerms")
        return 1

    result = {}
    for item in terms:
        key = item.get("Term")
        languages = item.get("Languages", [])
        if key is None:
            continue
        if len(languages) > ENGLISH_INDEX:
            result[key] = languages[ENGLISH_INDEX]
        else:
            result[key] = ""

    print(f"Извлечено записей: {len(result)}", flush=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Сохранено в: {output_path}", flush=True)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
