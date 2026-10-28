"""
Нормализует JSONL-файл: читает все JSON-объекты из исходника
(игнорируя форматирование, переносы, markdown-обёртки) и переписывает
их по одному на строку.

Использование: python fix_jsonl.py input.jsonl output.jsonl
"""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]

with open(src, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Убираем markdown-обёртки, если копировали из чата
for fence in ('```jsonl', '```json', '```'):
    content = content.replace(fence, '')

decoder = json.JSONDecoder()
records = []
idx = 0
errors = []

while idx < len(content):
    # пропускаем пробелы/переносы
    while idx < len(content) and content[idx].isspace():
        idx += 1
    if idx >= len(content):
        break

    try:
        obj, end = decoder.raw_decode(content, idx)
        records.append(obj)
        idx = end
    except json.JSONDecodeError as e:
        # запоминаем ошибку и пропускаем строку
        line_end = content.find('\n', idx)
        if line_end == -1:
            break
        errors.append(f'  at char {idx}: {e.msg} — preview: {content[idx:idx+60]!r}')
        idx = line_end + 1

with open(dst, 'w', encoding='utf-8') as f:
    for obj in records:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')

print(f'OK: {len(records)} records written to {dst}')
if errors:
    print(f'WARN: {len(errors)} unparsable chunks:')
    for err in errors[:5]:
        print(err)