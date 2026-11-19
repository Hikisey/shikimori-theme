#!/usr/bin/env python3
"""Сборка темы: модули из src/ (порядок — src/manifest.txt) -> css/part_NN.css.

Модули склеиваются в порядке манифеста, из потока убираются комментарии
(в src/ они остаются; Шикимори всё равно вырезает их при загрузке, а в лимит
размера файла они входили), и поток режется на части между
правилами верхнего уровня: часть набирается, пока не превысит --max байт
(по умолчанию 155 000). Модуль может начаться в одной части и кончиться в
следующей. Каскад от нарезки не меняется: part_01 + part_02 + … == модули подряд.

    python3 tools/build.py                   # пересобрать css/
    python3 tools/build.py --version 1.4.0  # заодно поставить версию в подвал
    python3 tools/build.py --out /tmp/x      # собрать в другую папку (css/ не трогать)

Пределы Шикимори (см. docs/ARCHITECTURE.md, «пределы импорта»):
- обрабатываются только первые ~6 @import, включая 2 из css-club → частей темы не больше 4;
- файл ~231 КБ уже не импортировался (225 КБ — ещё да) → части ≤ 155 КБ,
  жёсткий предел скрипта 160 КБ.

В начало каждой части ставится метка --sg-pN: "" (N — номер части). Блок
в site.css показывает в углу экрана, какая часть не загрузилась.
"""
import argparse, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARD_LIMIT = 160_000   # байт на часть; ~231 КБ Шикимори уже не импортировал
MAX_PARTS = 4          # Шикимори берёт только ~6 первых @import, 2 из них — css-club
RAW = 'https://raw.githubusercontent.com/Hikisey/shikimori-theme/{tag}/css/{name}'


def modules():
    man = os.path.join(ROOT, 'src', 'manifest.txt')
    out = []
    for line in open(man, encoding='utf-8'):
        line = line.split('#', 1)[0].strip()
        if line:
            p = os.path.join(ROOT, 'src', line)
            if not os.path.isfile(p):
                sys.exit(f'нет модуля из манифеста: src/{line}')
            out.append(p)
    known = {os.path.abspath(p) for p in out}
    for p in glob.glob(os.path.join(ROOT, 'src', '**', '*.css'), recursive=True):
        if os.path.abspath(p) not in known:
            print(f'внимание: src/{os.path.relpath(p, os.path.join(ROOT, "src"))} нет в manifest.txt — в сборку не попадёт')
    return out


def top_level_cuts(s):
    """Позиции сразу после '}' на глубине 0 (вне комментариев и строк)."""
    cuts, depth, i, n = [], 0, 0, len(s)
    while i < n:
        c = s[i]
        if s.startswith('/*', i):
            j = s.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in '"\'':
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == '\\' else 1
            i = j + 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                sys.exit(f'лишняя }} около символа {i}')
            if depth == 0:
                cuts.append(i + 1)
        i += 1
    if depth != 0:
        sys.exit('незакрытая { — проверьте последний изменённый модуль')
    return cuts


def strip_comments(s):
    """Убирает комментарии вне строк. Комментарий на отдельной строке
    уходит вместе со строкой; внутри строки — вместе с пробелами после него
    (так же, как это делает фильтр Шикимори). Отступы и переносы остаются."""
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in '"\'':
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == '\\' else 1
            out.append(s[i:j + 1]); i = j + 1
            continue
        if s.startswith('/*', i):
            j = s.find('*/', i + 2)
            j = n if j < 0 else j + 2
            line_start = ''.join(out).rfind('\n') + 1 if out else 0
            before = ''.join(out)[line_start:]
            k = j
            while k < n and s[k] in ' \t':
                k += 1
            if before.strip() == '' and (k >= n or s[k] == '\n'):
                joined = ''.join(out)[:line_start]
                out = [joined]
                i = k + 1
            else:
                i = k
            continue
        out.append(c); i += 1
    t = ''.join(out)
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t


def split(s, limit):
    cuts = top_level_cuts(s) + [len(s)]
    parts, start, last = [], 0, 0
    for c in cuts:
        if len(s[start:c].encode()) > limit and last > start:
            parts.append(s[start:last])
            start = last
        last = c
    parts.append(s[start:])
    return [p.strip('\n') + '\n' for p in parts if p.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--version', help='версия для подвала, например 1.4.0')
    ap.add_argument('--max', type=int, default=155_000, help='наибольший размер части в байтах (по умолчанию 155000)')
    ap.add_argument('--out', default=os.path.join(ROOT, 'css'))
    a = ap.parse_args()
    if a.max > HARD_LIMIT:
        sys.exit(f'--max больше {HARD_LIMIT}: большие файлы Шикимори не импортирует')
    mods = modules()
    if a.version:
        hit = 0
        for p in mods:
            t = open(p, encoding='utf-8').read()
            t2, n = re.subn(r'--theme-version: "[^"]*";', f'--theme-version: "{a.version}";', t)
            if n:
                open(p, 'w', encoding='utf-8').write(t2)
                hit += n
        if hit != 1:
            sys.exit(f'--theme-version найден {hit} раз(а), ожидался ровно 1')
    texts = [open(p, encoding='utf-8').read().rstrip('\n') + '\n\n' for p in mods]
    s = ''.join(texts)
    top_level_cuts(s)  # проверка скобок
    s = strip_comments(s)
    top_level_cuts(s)
    vm = re.search(r'--theme-version: "([^"]*)"', s)
    ver = vm.group(1) if vm else 'X.Y.Z'
    banner = f'/* shiki glass v{ver} — тема и обновления: https://github.com/Hikisey/shikimori-theme */\n'
    pack_limit = a.max - len(banner.encode()) - 40
    parts = split(s, pack_limit)
    os.makedirs(a.out, exist_ok=True)
    for old in glob.glob(os.path.join(a.out, 'part_*.css')):
        os.remove(old)
    names = []
    for k, p in enumerate(parts, 1):
        name = f'part_{k:02d}.css'
        p = banner + f'html:root {{ --sg-p{k}: ""; }}\n\n' + p
        open(os.path.join(a.out, name), 'w', encoding='utf-8').write(p)
        size = len(p.encode())
        print(f'{name}  {size:6d} байт  {p.count(chr(10)):5d} строк')
        if size > HARD_LIMIT:
            sys.exit(f'{name}: больше {HARD_LIMIT} байт — Шикимори может не импортировать')
        names.append(name)
    if len(names) > MAX_PARTS:
        sys.exit(f'частей {len(names)} > {MAX_PARTS}: Шикимори обрабатывает только ~6 @import (2 из них css-club)')
    room = MAX_PARTS * a.max - sum(os.path.getsize(os.path.join(a.out, x)) for x in names)
    print(f'модулей: {len(mods)}, частей: {len(parts)}, всего {len(s.encode())} байт, запас {room} байт')
    if room < 5000:
        print('ВНИМАНИЕ: запас меньше 5 КБ — следующая правка может дать пятую часть')
    m = re.search(r'--theme-version: "([^"]*)"', s)
    tag = 'v' + m.group(1) if m else 'vX.Y.Z'
    print('\nстроки для «Внешнего вида сайта»:')
    for n in names:
        print(f'@import url("{RAW.format(tag=tag, name=n)}");')


main()
