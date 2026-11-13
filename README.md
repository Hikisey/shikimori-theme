# shikimori-theme

Тёмная тема для [Шикимори](https://shikimori.one): графит с алым акцентом, обои с плавным зумом, непрозрачная верхняя панель без мерцания, анимированные карточки аниме и читаемые настройки.

Спасибо [ed-main](https://github.com/ed-main) за основу.

## Как подключить

Откройте «Настройки → Внешний вид сайта» и вставьте:

```css
@import url("https://css-club.web.app/css/CodeMirror_dark.css");
@import url("https://css-club.web.app/css/custom_posters.min.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_1.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_2.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_3.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_4mob.css");
```

`CodeMirror_dark.css` делает тёмным редактор кода в настройках. `custom_posters.min.css` нужен для замены постеров персонажей. Эти две строки должны стоять в «Внешнем виде сайта», а не внутри файлов темы: Шикимори вырезает `@import` из подключённых файлов.

Всё остальное — обои, постеры, баннер, скругления и анимации — уже внутри темы.

## Палитра

Тема работает и без своей палитры, цвета по умолчанию уже заданы. Чтобы поменять цвета, добавьте под строками `@import` блок с переменными. Значения пишутся как три числа R, G, B через запятую, без `rgb()`:

```css
@media screen and (min-width: 1px) {
  html:root {
    --light-color: 236, 240, 247;   /* основной текст */
    --dark-color: 170, 178, 192;    /* вторичный текст, подсказки */
    --bright-color: 232, 108, 108;  /* акцент: ссылки, подсветка */
    --hover-color: 232, 108, 108;   /* цвет при наведении */
    --buttoms-color: 178, 58, 64;   /* кнопки */
    --block-color: 30, 34, 42;      /* фон блоков */
    --menu-back: 20, 22, 28;        /* тёмные подложки, затемнение обоев */
    --menu-bar: 18, 20, 26;         /* верхняя панель */
    --menu-bar-hover: 26, 29, 37;   /* панель под курсором и её меню */
    --popup-color: 38, 43, 54;      /* выпадающие списки */
  }
}
```

Обёртка `@media` обязательна. Без неё Шикимори применит ваш CSS только на экранах шире 1024px.

Полная палитра с пояснением к каждой переменной есть в файле [`site.css`](site.css).

## Дополнительно

Эти блоки можно добавить в «Внешний вид сайта»:

**Полупрозрачная рамка вокруг страницы:**

```css
@media (min-width: 1200px) {
  .l-page { outline: 20px solid rgba(255, 255, 255, 0.3); margin-bottom: 20px; }
}
```

**Вернуть всплывающие карточки с описанием при наведении на аниме** (в теме они скрыты):

```css
.tooltip { visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }
.tooltip * { visibility: inherit !important; pointer-events: auto !important; }
```

## Если изменения из репозитория не видны на сайте

Шикимори хранит подключённые файлы у себя до 8 часов. Чтобы обновить их сразу:

1. Откройте <https://shikimori.one/tests/reset_styles_cache>.
2. Вставьте ссылку на изменённый файл, например `https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_4mob.css`, и отправьте. Сделайте так для каждого изменённого файла.
3. Обновите страницу с Ctrl+Shift+R.

Символ `@` в адресах `url(...)` Шикимори вырезает, поэтому ссылки на картинки должны быть без него.

## Пример «Внешнего вида сайта»

Готовый файл со всеми строками `@import`, палитрой и дополнительными блоками в комментариях: [`site.css`](site.css).
