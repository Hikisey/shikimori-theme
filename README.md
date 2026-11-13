# shikimori-theme

Тема для [Шикимори](https://shikimori.one): база **E-design** от [ed-main](https://github.com/ed-main/ed-main.github.io) с исправленными багами, плюс мои обои (`bg.webp`).

## Авторство

Весь исходный код темы в папке `css/` взят у **ed-main**, из файлов [`cssfiles/main_code_*.css`](https://github.com/ed-main/ed-main.github.io/tree/master/cssfiles). Их сборщик основан на [shiki-theme](https://github.com/grin3671/shiki-theme) от grin3671. Права на исходный код принадлежат их авторам. В оригинальном репозитории нет файла лицензии, поэтому это не форк под свободной лицензией, а копия с исправлениями и указанием автора. Если автор против, файлы будут убраны.

Каждое изменение в файлах помечено комментарием:

- `FIX:` — исправленный баг. Рядом в комментарии записано, как было.
- `ОТКЛЮЧЕНО:` — функция выключена. Рядом написано, как её вернуть.
- `НОВОЕ:` — раздел с исправлениями в конце `main_code_4mob.css`.

## Что исправлено

- **Верхняя панель** больше не мерцает и не становится прозрачной при наведении, а тень под ней не пропадает. Фон стал непрозрачным, при наведении панель плавно и едва заметно светлеет.
- **Выпадающие меню панели** теперь непрозрачные и того же цвета, что панель. Пункт под курсором мягко подсвечивается.
- **Карточки аниме** при наведении поднимаются целиком, обложка вместе с подложкой. Картинка внутри слегка приближается, а название подсвечивается акцентом.
- **Выпадающие списки в фильтрах** каталога больше не прозрачные.
- **Настройки** стали читаемыми. Подсказки под полями были окрашены цветом теней и пропадали на тёмной палитре. Поля ввода стали видимыми, при фокусе у них появляется подсветка.

## Что отключено

- **Всплывающая мини-карточка** при наведении на аниме, персонажей и т.п. (окно с крестиком). Чтобы вернуть её, добавьте к себе в CSS:

  ```css
  .tooltip { visibility: visible !important; pointer-events: auto !important; }
  .tooltip * { visibility: inherit !important; pointer-events: auto !important; }
  ```

- **Серость значков франшиз при наведении** в профиле. Чтобы вернуть, добавьте к себе в CSS:

  ```css
  #profiles_show.p-profiles-show .achievements .cc-franchises .b-badge:hover {
    filter: brightness(80%) contrast(102%) grayscale(80%);
  }
  ```

## Как подключить

Вставьте в начало поля «Настройки → Внешний вид сайта»:

```css
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_1.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_2.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_3.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_4mob.css");
```

Ниже задайте свою палитру. Это rgb-тройки без `rgb()`:

```css
@media screen and (min-width: 1px) {
  html:root {
    --light-color: 236, 240, 247;   /* основной текст */
    --dark-color: 170, 178, 192;    /* вторичный текст и подсказки */
    --bright-color: 232, 108, 108;  /* акцент */
    --menu-back: 20, 22, 28;        /* тёмные подложки */
    --popup-color: 38, 43, 54;      /* выпадающие списки */
    --menu-bar: 18, 20, 26;         /* верхняя панель (необязательно) */
    --menu-bar-hover: 26, 29, 37;   /* панель под курсором и её меню (необязательно) */
  }
}
```

Все переменные темы: `--white-color`, `--light-color`, `--dark-color`, `--bright-color`, `--dull-color`, `--input-color`, `--hover-bottoms-1`, `--buttoms-color`, `--hover-buttoms-2`, `--very-high-rating`, `--high-rating`, `--average-rating`, `--small-rating`, `--time-filled`, `--time-empty`, `--anime-inprocess`, `--anime-complete`, `--manga-inprocess`, `--manga-complete`, `--hover-color`, `--shadows-color`, `--block-color`, `--menu-back`, `--nick-cover`, `--popup-color`, `--hundred` (обычно 1).

Важно: из адресов в `url(...)` Шикимори вырезает символ `@`, поэтому ссылка на картинку не должна его содержать. Например, ссылку jsDelivr с версией вида `...@main/...` писать нельзя.

## Если изменения в репозитории не видны на сайте

Шикимори кеширует подключённые файлы примерно на 8 часов. Чтобы обновить их сразу:

1. Откройте <https://shikimori.one/tests/reset_styles_cache>.
2. Вставьте туда ссылку на файл (например `https://raw.githubusercontent.com/Hikisey/shikimori-theme/main/css/main_code_3.css`) и отправьте форму. Повторите это для каждого изменённого файла.
3. Обновите страницу сайта с Ctrl+Shift+R.

## Обои

`bg.webp` — мои обои. Ссылка для CSS: `https://cdn.jsdelivr.net/gh/Hikisey/shikimori-theme/bg.webp`
