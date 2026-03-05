#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт подставляет русские переводы из localization/russian_keys.json
вместо английских текстов в I2Languages.json и сохраняет результат в новый файл.
Исходный I2Languages.json не изменяется.

Использование:
  python apply_russian_to_i2languages.py [путь/к/I2Languages.json]

  Если путь не указан, ищет I2Languages.json в текущей папке и в extract_english_keys/.
"""

import json
import os
import sys
from typing import Optional

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Индекс английского в массиве Languages (0=简体中文, 1=English, 2=日本語, 3=繁体中文)
ENGLISH_INDEX = 1


def find_i2languages(script_dir: str, explicit_path: Optional[str]) -> Optional[str]:
    """Возвращает путь к I2Languages.json."""
    if explicit_path and os.path.isfile(explicit_path):
        return explicit_path
    candidates = [
        os.path.join(script_dir, "I2Languages.json"),
        os.path.join(script_dir, "extract_english_keys", "I2Languages.json"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    i2_path = find_i2languages(script_dir, sys.argv[1] if len(sys.argv) > 1 else None)
    if not i2_path:
        print("Файл I2Languages.json не найден. Укажите путь явно: python apply_russian_to_i2languages.py <путь>")
        return 1

    ru_keys_path = os.path.join(script_dir, "localization", "russian_keys.json")
    if not os.path.isfile(ru_keys_path):
        print(f"Файл не найден: {ru_keys_path}")
        return 1

    # Выходной файл — рядом с исходным, с суффиксом _ru
    base, ext = os.path.splitext(i2_path)
    out_path = base + "_ru" + ext

    print("Загрузка I2Languages.json...", flush=True)
    with open(i2_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Загрузка russian_keys.json...", flush=True)
    with open(ru_keys_path, "r", encoding="utf-8") as f:
        russian_keys = json.load(f)

    terms = data.get("m_Structure", {}).get("mSource", {}).get("mTerms", [])
    if not terms:
        print("Не найдено m_Structure.mSource.mTerms в I2Languages.json")
        return 1

    replaced = 0
    for item in terms:
        key = item.get("Term")
        if key is None:
            continue
        if key not in russian_keys:
            continue
        languages = item.get("Languages", [])
        # Расширяем массив до нужного индекса при необходимости
        while len(languages) <= ENGLISH_INDEX:
            languages.append("")
        languages[ENGLISH_INDEX] = russian_keys[key]
        item["Languages"] = languages
        replaced += 1

    print(f"Подставлено русских переводов: {replaced} из {len(terms)} терминов", flush=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
