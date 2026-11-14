#!/usr/bin/env bash
# Сборка: src/main_code_*.css (порядок важен) -> css/part_NN.css, каждая часть <= 80 000 байт.
# Шикимори на v1.2.21–v1.2.22 не смог импортировать файл ~231 КБ, а файлы ~100 КБ грузил,
# поэтому выпускаем части с запасом. Каскад не меняется: части — это те же правила подряд.
#   VERSION=1.2.23 bash tools/build.sh
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -n "${VERSION:-}" ]; then
  sed -i "s/--theme-version: \"[^\"]*\";/--theme-version: \"$VERSION\";/" src/main_code_2.css
fi
rm -f css/part_*.css
python3 tools/split_css.py --max "${MAX_BYTES:-80000}" --out css \
  src/main_code_1.css src/main_code_2.css src/main_code_3.css src/main_code_4mob.css
echo
echo "строки для «Внешнего вида сайта» (TAG = тег релиза):"
for f in css/part_*.css; do echo "@import url(\"https://raw.githubusercontent.com/Hikisey/shikimori-theme/TAG/$f\");"; done
