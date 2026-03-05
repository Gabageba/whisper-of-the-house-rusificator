#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт подставляет русские переводы из localization/russian_keys.json
вместо английских текстов в I2Languages-resources.assets-2800.txt и сохраняет
результат в новый файл. Запись языка English меняется на Russian (ru).
Исходный файл не изменяется. Формат строк и тегов сохраняется как в оригинале.

Использование:
  python apply_russian_to_assets_txt.py [путь/к/I2Languages-resources.assets-2800.txt]
"""

import json
import os
import re
import sys
from typing import Optional

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Индекс английского в массиве Languages (0=简体中文, 1=English, 2=日本語, 3=繁体中文)
ENGLISH_INDEX = 1


def escape_value_for_txt(value: str) -> str:
    """В формате .txt кавычка внутри значения удваивается ("")."""
    return value.replace('"', '""')


def find_assets_txt(script_dir: str, explicit_path: Optional[str]) -> Optional[str]:
    """Возвращает путь к I2Languages-resources.assets-2800.txt."""
    if explicit_path and os.path.isfile(explicit_path):
        return explicit_path
    default = os.path.join(script_dir, "I2Languages-resources.assets-2800.txt")
    if os.path.isfile(default):
        return default
    return None


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = find_assets_txt(script_dir, sys.argv[1] if len(sys.argv) > 1 else None)
    if not input_path:
        print("Файл I2Languages-resources.assets-2800.txt не найден. Укажите путь явно.")
        return 1

    ru_keys_path = os.path.join(script_dir, "localization", "russian_keys.json")
    if not os.path.isfile(ru_keys_path):
        print(f"Файл не найден: {ru_keys_path}")
        return 1

    base, ext = os.path.splitext(input_path)
    out_path = base + "_ru" + ext

    print("Загрузка russian_keys.json...", flush=True)
    with open(ru_keys_path, "r", encoding="utf-8") as f:
        russian_keys = json.load(f)

    print("Чтение assets-файла...", flush=True)
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Паттерны: Term = "key", строка data для Languages [1], mLanguages Name/Code
    re_term = re.compile(r'^\s+1 string Term = "([^"]*)"\s*$')
    re_lang_data = re.compile(r'^(\s+)1 string data = "(.*)"\s*$')  # group(1)=отступ, group(2)=значение (может содержать "")
    re_name_english = re.compile(r'^(\s+)1 string Name = "English"\s*$')
    re_code_en = re.compile(r'^(\s+)1 string Code = "en"\s*$')

    in_languages = False
    lang_slot = -1
    current_key = None
    replaced = 0
    output_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip("\n\r")

        # Конец блока Languages — сбрасываем состояние при новом термине
        term_match = re_term.match(stripped)
        if term_match:
            current_key = term_match.group(1)
            in_languages = False
            lang_slot = -1

        # Вход в массив Languages (сразу после "0 string Languages")
        if "0 string Languages" in stripped and current_key is not None:
            in_languages = True
            lang_slot = -1

        # Индексы [0] [1] [2] [3] внутри Languages
        if in_languages and re.match(r'^\s+\[\d+\]\s*$', stripped):
            idx_match = re.match(r'^\s+\[(\d+)\]\s*$', stripped)
            if idx_match:
                lang_slot = int(idx_match.group(1))

        # Строка "1 string data = "..." — подставляем русский только для [1]
        if in_languages and lang_slot == ENGLISH_INDEX:
            data_match = re_lang_data.match(stripped)
            if data_match:
                indent, value_part = data_match.group(1), data_match.group(2)
                # В файле кавычка в значении записана как "" — восстанавливаем одну "
                value = value_part.replace('""', '"')
                if current_key and current_key in russian_keys:
                    new_value = russian_keys[current_key]
                    new_value_escaped = escape_value_for_txt(new_value)
                    stripped = f'{indent}1 string data = "{new_value_escaped}"'
                    replaced += 1
                in_languages = False
                lang_slot = -1

        # mLanguages: замена English -> Russian, en -> ru (только в блоке [1] LanguageData)
        if re_name_english.match(stripped):
            stripped = re_name_english.sub(r'\g<1>1 string Name = "Russian"', stripped)
        if re_code_en.match(stripped):
            stripped = re_code_en.sub(r'\g<1>1 string Code = "ru"', stripped)

        output_lines.append(stripped + "\n")
        i += 1

    print(f"Подставлено русских переводов: {replaced}", flush=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(output_lines)
    print(f"Сохранено в: {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
