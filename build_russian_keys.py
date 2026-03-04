# -*- coding: utf-8 -*-
"""
Собирает russian_keys.json из english_keys.json:
- Для ключей QuestCompletionPrompt, LevelQuestInfo, QuestDescription2, QuestLetter,
  CharacterName, Image, Tip, QuestTip, Mail, ItemInfo, Dialogues — подставляются
  естественные русские переводы из russian_translations.py (без сухого машинного перевода).
- Для остальных ключей используется текст из english_keys.json (можно потом перевести
  отдельно или другим способом).
Запуск: py -u build_russian_keys.py
"""

import json
import os
import sys

# Сразу выводим, что скрипт запустился
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

try:
    from russian_translations import get_all_natural_translations
except ImportError:
    get_all_natural_translations = lambda: {}

try:
    from item_name_glossary import build_item_name_dict
except ImportError:
    build_item_name_dict = lambda en: {}


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "english_keys.json")
    output_path = os.path.join(script_dir, "russian_keys.json")

    if not os.path.exists(input_path):
        print(f"Файл не найден: {input_path}", flush=True)
        return 1

    print("Загрузка english_keys.json...", flush=True)
    with open(input_path, "r", encoding="utf-8") as f:
        en = json.load(f)

    ru = get_all_natural_translations()
    item_ru = build_item_name_dict(en)
    print(f"Загружено естественных переводов: {len(ru)}", flush=True)
    print(f"Переводов названий предметов (ItemName): {len(item_ru)}", flush=True)

    result = {}
    replaced = 0
    for key, value in en.items():
        if key in ru and ru[key]:
            result[key] = ru[key]
            replaced += 1
        elif key in item_ru and item_ru[key]:
            result[key] = item_ru[key]
            replaced += 1
        else:
            result[key] = value

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Подставлено русских строк: {replaced}", flush=True)
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
