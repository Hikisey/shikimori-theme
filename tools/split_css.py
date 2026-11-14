#!/usr/bin/env python3
"""Склеивает файлы темы по порядку и режет на части не больше --max байт.

Режем только между правилами верхнего уровня (вне { }), поэтому каскад
не меняется: part_01 + part_02 + ... == исходные файлы подряд.

    python3 tools/split_css.py --max 80000 --out css a.css b.css ...
"""
import argparse, os, re, sys

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
            if depth == 0:
                cuts.append(i + 1)
        i += 1
    if depth != 0:
        sys.exit('unbalanced braces')
    return cuts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max', type=int, default=80000)
    ap.add_argument('--out', default='css')
    ap.add_argument('--prefix', default='part_')
    ap.add_argument('files', nargs='+')
    a = ap.parse_args()
    s = ''.join(open(f, encoding='utf-8').read().rstrip('\n') + '\n\n' for f in a.files)
    cuts = top_level_cuts(s) + [len(s)]
    parts, start, last = [], 0, 0
    for c in cuts:
        if len(s[start:c].encode()) > a.max and last > start:
            parts.append(s[start:last]); start = last
        last = c
    parts.append(s[start:])
    os.makedirs(a.out, exist_ok=True)
    for k, p in enumerate(parts, 1):
        p = p.strip('\n') + '\n'
        name = os.path.join(a.out, f'{a.prefix}{k:02d}.css')
        open(name, 'w', encoding='utf-8').write(p)
        print(name, len(p.encode()), 'bytes', p.count('\n'), 'lines')
        if len(p.encode()) > a.max:
            sys.exit(f'{name}: одно правило больше --max')

main()
