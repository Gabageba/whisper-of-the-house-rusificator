#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создаёт новый дамп на основе I2Languages-resources.assets-2800.txt:
- Экранирует кавычки и обратные слеши во всех строках string data для UABEA
- Заменяет английские тексты (язык [1]) на русские из localization/russian_keys.json
- Теги (<PlayerName> и т.д.) не меняются — берутся из значения в JSON как есть
- В блоке mLanguages для слота [1] меняет только Name "English" → "Русский" (Code и остальное не трогает)

Использование:
  python build_ru_dump.py [input.txt] [output.txt]
  По умолчанию: I2Languages-resources.assets-2800.txt -> I2Languages-resources.assets-2800_ru_new.txt
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "I2Languages-resources.assets-2800.txt"
DEFAULT_OUTPUT = SCRIPT_DIR / "I2Languages-resources.assets-2800_ru_new.txt"
RUSSIAN_KEYS_PATH = SCRIPT_DIR / "localization" / "russian_keys.json"

# Индекс английского в массиве Languages (0=简体中文, 1=English, 2=日本語, 3=繁体中文)
# В новом файле в этот слот подставляем русский
ENGLISH_SLOT_INDEX = 1


def escape_for_uabea(s: str) -> str:
    """Экранирует строку для формата UABEA: \\, \", перевод строки -> \\n."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    input_path = Path(sys.argv[1]) if len(sys.argv) >= 2 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_OUTPUT

    if not input_path.is_file():
        print(f"Файл не найден: {input_path}", flush=True)
        return 1

    if not RUSSIAN_KEYS_PATH.is_file():
        print(f"Файл не найден: {RUSSIAN_KEYS_PATH}", flush=True)
        return 1

    print("Загрузка russian_keys.json...", flush=True)
    with open(RUSSIAN_KEYS_PATH, "r", encoding="utf-8") as f:
        ru_keys = json.load(f)

    print(f"Чтение дампа: {input_path}", flush=True)
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Состояние парсера
    current_term = None
    in_languages = False
    current_lang_index = -1
    in_mLanguages = False
    mLanguages_slot = -1
    # Паттерн: строка с "1 string data = " в блоке Languages
    re_string_data = re.compile(r'^(\s*1 string data = )"(.*)"\s*$', re.DOTALL)
    re_term = re.compile(r'^\s+1 string Term = "(.*)"\s*$')
    re_lang_slot = re.compile(r'^\s+\[(\d+)\]\s*$')
    re_section = re.compile(r'^\s+0 (string Languages|vector Flags|string Languages_Touch)\s*$')
    re_mLanguages_start = re.compile(r'^\s+0 LanguageData mLanguages\s*$')
    re_mLanguages_slot = re.compile(r'^\s{4}\[(\d+)\]\s*$')
    re_after_mLanguages = re.compile(r'^\s{2}[01] (?:UInt8|int|float|vector|string)\s')
    re_name_english = re.compile(r'^(\s*1 string Name = )"English"\s*$')

    result = []
    replaced_count = 0
    escaped_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        orig_line = line

        # Текущий термин (ключ для подстановки русского)
        term_match = re_term.match(line)
        if term_match:
            current_term = term_match.group(1)
            result.append(line)
            i += 1
            continue

        # Секция: Languages / Flags / Languages_Touch
        section_match = re_section.match(line)
        if section_match:
            name = section_match.group(1)
            in_languages = name == "string Languages"
            if not in_languages:
                current_lang_index = -1
            result.append(line)
            i += 1
            continue

        # Блок mLanguages: слоты [0]..[3] с отступом 4 пробела (до проверки общих слотов mTerms — там 8 пробелов)
        if in_mLanguages and re_mLanguages_slot.match(line):
            mLanguages_slot = int(re_mLanguages_slot.match(line).group(1))
            result.append(line)
            i += 1
            continue
        # Выход из блока mLanguages (следующее поле объекта)
        if in_mLanguages and re_after_mLanguages.match(line):
            in_mLanguages = False
            mLanguages_slot = -1
        # Имя языка в mLanguages для слота [1]: только Name English -> Russian
        if in_mLanguages and mLanguages_slot == 1 and re_name_english.match(line):
            result.append(re_name_english.sub(r'\1"Русский"\n', line))
            i += 1
            continue

        # Индекс слота языка [0], [1], [2], [3] в mTerms
        slot_match = re_lang_slot.match(line)
        if slot_match:
            current_lang_index = int(slot_match.group(1))
            result.append(line)
            i += 1
            continue

        # Строка со значением "1 string data = "..."
        data_match = re_string_data.match(line)
        if data_match:
            prefix = data_match.group(1)
            raw_value = data_match.group(2)
            # Рассимволить экранирование при чтении (на случай если в исходнике уже есть \")
            value = raw_value.replace('\\"', '"').replace("\\\\", "\\")

            use_russian = (
                in_languages
                and current_lang_index == ENGLISH_SLOT_INDEX
                and current_term is not None
                and current_term in ru_keys
            )
            if use_russian:
                value = ru_keys[current_term]
                replaced_count += 1
            value_escaped = escape_for_uabea(value)
            escaped_count += 1
            result.append(prefix + '"' + value_escaped + '"\n')
            i += 1
            continue

        # Вход в блок mLanguages
        if re_mLanguages_start.match(line):
            in_mLanguages = True
            result.append(line)
            i += 1
            continue

        result.append(line)
        i += 1

    print(f"Запись в {output_path}...", flush=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(result)

    print(f"Готово. Подставлено русских строк: {replaced_count}, экранировано строк: {escaped_count}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
