#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Исправляет дамп UABEA для корректной загрузки (ошибка "Length cannot be less than zero"):
# 1. Многострочные значения string data — в одну строку с \n
# 2. Строки с "" в начале (китайские кавычки, HANDCRAFT) — экранирование
# 3. Тройные кавычки в одну пару с экранированием внутренних кавычек

import sys

INPUT_FILE = "I2Languages-resources.assets-2800_ru.txt"
OUTPUT_FILE = "I2Languages-resources.assets-2800_ru_fixed.txt"


def process_file(in_path: str, out_path: str) -> None:
    with open(in_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Случай 1: многострочное значение — строка с """ без закрывающих """ и следующая с """
        if 'string data = """' in line and not line.rstrip().endswith('"""'):
            if i + 1 < len(lines) and lines[i + 1].strip().endswith('"""'):
                part1 = line[line.find('"""') + 3 :].rstrip()
                part2 = lines[i + 1].strip()[:-3]
                content = part1 + "\\n" + part2
                content = content.replace("\\", "\\\\").replace('"', '\\"')
                prefix = line[: line.find('string data = """')] + 'string data = "'
                result.append(prefix + content + '"\n')
                i += 2
                continue

        # Случай 2: строка с "" в начале (не """) — например ""栗绿之境"枕头" или ""HANDCRAFT""
        if 'string data = ""' in line and 'string data = """' not in line and line.rstrip().endswith('"'):
            idx = line.find('string data = ""')
            prefix = line[: idx] + 'string data = "'
            # Контент: от первой " значения до последней (не включая закрывающую)
            content = line[idx + len('string data = "'): line.rfind('"')].rstrip()
            content = content.replace("\\", "\\\\").replace('"', '\\"')
            result.append(prefix + content + '"\n')
            i += 1
            continue

        # Случай 3: тройные кавычки в одной строке """...""" (закрытие тройное)
        if 'string data = """' in line and line.rstrip().endswith('"""'):
            prefix = line[: line.find('string data = """')] + 'string data = "'
            rest = line[line.find('"""') + 3 :]
            if rest.rstrip().endswith('"""'):
                content = rest.rstrip()[:-3]
            else:
                content = rest.rstrip().rstrip('"')
            content = content.replace("\\", "\\\\").replace('"', '\\"')
            result.append(prefix + content + '"\n')
            i += 1
            continue

        # Случай 4: """ в начале, но в конце одна " (в тексте есть "")
        if 'string data = """' in line and line.rstrip().endswith('"') and not line.rstrip().endswith('"""'):
            prefix = line[: line.find('string data = """')] + 'string data = "'
            content = line[line.find('"""') + 3 : line.rfind('"')].rstrip()
            content = content.replace("\\", "\\\\").replace('"', '\\"')
            result.append(prefix + content + '"\n')
            i += 1
            continue

        # Случай 5: многострочное с """ в начале, продолжение на следующей строке (без тройного в конце первой)
        if 'string data = """' in line and not line.rstrip().endswith('"""'):
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("["):
                # Собираем строки до той, что заканчивается на """
                parts = [line[line.find('"""') + 3 :].rstrip()]
                j = i + 1
                while j < len(lines) and not lines[j].strip().endswith('"""'):
                    parts.append(lines[j].rstrip())
                    j += 1
                if j < len(lines):
                    parts.append(lines[j].strip()[:-3])
                    content = "\\n".join(parts)
                    content = content.replace("\\", "\\\\").replace('"', '\\"')
                    prefix = line[: line.find('string data = """')] + 'string data = "'
                    result.append(prefix + content + '"\n')
                    i = j + 1
                    continue
            # иначе не многострочное — обработаем в случае 4 при следующем проходе не получится, уже обработано
            pass

        result.append(line)
        i += 1

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(result)
    print(f"Готово: записано в {out_path}")


def main():
    in_path = sys.argv[1] if len(sys.argv) >= 2 else INPUT_FILE
    out_path = sys.argv[2] if len(sys.argv) >= 3 else OUTPUT_FILE
    process_file(in_path, out_path)
    print("Замените исходный файл на исправленный и снова загрузите в UABEA.")


if __name__ == "__main__":
    main()
