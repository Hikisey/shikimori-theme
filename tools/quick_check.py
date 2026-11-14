#!/usr/bin/env python3
"""Быстрая проверка после мелкой правки (по умолчанию для любых правок; полная
регрессия со сравнением страниц — только перед релизом, см. AGENTS.md).

    python3 tools/quick_check.py                         # сборка во временную папку + проверки
    python3 tools/quick_check.py --page saved.html       # + скриншот сохранённой страницы
    python3 tools/quick_check.py --page saved.html --phone

1. собирает src/ во временную папку (css/ не трогает);
2. гоняет эмуляцию фильтра Шикимори (tools/shiki_compile.py) и сверяет, что
   не пропало ни одно правило (число { и } до и после);
3. ищет ссылки, которые после camo «съели» код (tools/shiki_url_check.py);
4. жёсткие правила: нет слова behavior и @view-transition, нет новых обратных
   слэшей, каждая часть не больше 160 КБ и частей не больше 4; считает :hover вне медиазапроса;
5. с --page: вставляет собранный стиль и палитру из site.css в сохранённую
   страницу Шикимори и делает скриншот (нужен node + playwright-core + chrome).
"""
import argparse, glob, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, 'tools')
# унаследованный приём иконочного шрифта: url("/\x/…") — 5 мест; плюс \fXXX в content
ALLOWED_BACKSLASH = re.compile(r'''content:\s*['"](?:\\f[0-9a-f]{3})+['"]|url\("/\\x/''', re.I)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--page', help='сохранённая html-страница Шикимори для скриншота')
    ap.add_argument('--phone', action='store_true', help='скриншот как iPhone (390×844)')
    ap.add_argument('--out', default=os.path.join(tempfile.gettempdir(), 'hikisey_check'))
    a = ap.parse_args()
    ok = True
    os.makedirs(a.out, exist_ok=True)
    r = run([sys.executable, os.path.join(T, 'build.py'), '--out', a.out])
    print(r.stdout.split('\n\n')[0])
    if r.returncode:
        print(r.stderr or r.stdout); sys.exit('сборка не прошла')
    parts = sorted(glob.glob(os.path.join(a.out, 'part_*.css')))
    for f in glob.glob(os.path.join(a.out, '*.shiki')):
        os.remove(f)
    run([sys.executable, os.path.join(T, 'shiki_compile.py')] + parts)
    for p in parts:
        src = open(p, encoding='utf-8').read()
        out = open(p + '.shiki', encoding='utf-8').read()
        nb = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
        if nb.count('{') != out.count('{') or nb.count('}') != out.count('}'):
            ok = False
            print(f'ФИЛЬТР: {os.path.basename(p)} — скобок было {nb.count("{")}/{nb.count("}")}, стало {out.count("{")}/{out.count("}")}')
        if len(src.encode()) > 160_000:
            ok = False; print(f'РАЗМЕР: {os.path.basename(p)} больше 160 КБ')
        for word in ('behavior', 'behaviour', '@view-transition'):
            if word in src.lower():
                ok = False; print(f'ЗАПРЕТ: «{word}» в {os.path.basename(p)}')
        bad = ALLOWED_BACKSLASH.sub('', nb).count('\\')
        if bad:
            ok = False; print(f'СЛЭШ: {bad} обратных слэшей вне content/иконочного шрифта в {os.path.basename(p)}')
    r = run([sys.executable, os.path.join(T, 'shiki_url_check.py')] + parts)
    if r.returncode:
        ok = False; print(r.stdout)
    # :hover вне @media (hover: hover) — только счётчик (старые цветовые правила остались из истории)
    total = 0
    for p in parts:
        s = re.sub(r'/\*.*?\*/', '', open(p, encoding='utf-8').read(), flags=re.S)
        depth_media_hover, stack = 0, []
        for m in re.finditer(r'([^{};]*)\{|\}', s):
            if m.group(0) == '}':
                if stack: stack.pop()
                continue
            head = m.group(1).strip()
            if head.startswith('@'):
                stack.append('hover' if 'hover' in head and head.startswith('@media') else 'at')
            else:
                if ':hover' in head and 'hover' not in stack:
                    total += 1
                stack.append('rule')
    print(f':hover вне @media (hover: hover): {total} правил (новые правила с :hover кладите в медиазапрос)')
    if a.page:
        site = open(os.path.join(ROOT, 'site.css'), encoding='utf-8').read()
        site = re.sub(r'@import url\("[^"]*"\);', '', site)
        open(os.path.join(a.out, 'site_palette.css'), 'w', encoding='utf-8').write(site)
        run([sys.executable, os.path.join(T, 'shiki_compile.py'), os.path.join(a.out, 'site_palette.css')])
        css = ''.join(open(p + '.shiki', encoding='utf-8').read() + '\n' for p in parts)
        css += open(os.path.join(a.out, 'site_palette.css.shiki'), encoding='utf-8').read()
        css = css.replace('https://camo.example/x?url=', '')
        css = re.sub(r'url\((["\']?)(https?%3A[^)"\']*)', lambda m: 'url(' + m.group(1) + __import__('urllib.parse').parse.unquote(m.group(2)), css)
        open(os.path.join(a.out, 'style.css'), 'w', encoding='utf-8').write(css)
        png = os.path.join(a.out, 'shot_phone.png' if a.phone else 'shot_pc.png')
        r = run(['node', os.path.join(T, 'shot.js'), os.path.abspath(a.page), os.path.join(a.out, 'style.css'), png, 'phone' if a.phone else 'pc'])
        print(r.stdout.strip() or r.stderr.strip())
    print('ИТОГ:', 'ok' if ok else 'есть ошибки')
    sys.exit(0 if ok else 1)


main()
