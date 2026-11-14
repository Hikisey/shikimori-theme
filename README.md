# shiki glass

Тёмная тема для [Шикимори](https://shikimori.io): мягкое стекло, графит, алый акцент по умолчанию. Работает на ПК и на телефоне. Текущая версия **v1.4.0**.

![shiki glass: страница аниме](docs/screenshot.jpg)

![Главная](docs/home.jpg)
![Каталог с фильтром](docs/catalog.jpg)
![Профиль](docs/profile.jpg)
![Телефон](docs/phone.jpg)

Спасибо [ed-main](https://github.com/ed-main) за основу.

## Установка

1. Откройте [`site.css`](https://raw.githubusercontent.com/Hikisey/shikimori-theme/v1.4.0/site.css) и скопируйте весь текст.
2. На Шикимори: профиль → «Настройки» → «Внешний вид сайта».
3. Замените всё в поле стиля скопированным текстом, нажмите «Сохранить» и обновите страницу (Ctrl+Shift+R).

Строки подключения (они уже стоят в начале `site.css`; `@import` всегда идут первыми):

```css
@import url("https://css-club.web.app/css/CodeMirror_dark.css");
@import url("https://css-club.web.app/css/custom_posters.min.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/v1.4.0/css/part_01.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/v1.4.0/css/part_02.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/v1.4.0/css/part_03.css");
@import url("https://raw.githubusercontent.com/Hikisey/shikimori-theme/v1.4.0/css/part_04.css");
```

Чтобы обновиться, замените в этих строках номер версии на новый со страницы [Releases](https://github.com/Hikisey/shikimori-theme/releases). Если число файлов в новой версии другое, проще заново скопировать `site.css` (свою палитру сохраните).

Тема собрана ровно в 4 файла: Шикимори обрабатывает только первые ~6 строк `@import` (две из них — css-club), а файл больше ~230 КБ не импортирует. Поэтому каждая часть не больше 150 КБ, и лишних `@import` перед строками темы добавлять не стоит.

Если Шикимори пишет «Не удалось импортировать», вставьте ссылку из сообщения на странице [shikimori.io/tests/reset_styles_cache](https://shikimori.io/tests/reset_styles_cache) и сохраните стиль ещё раз.

## Как сменить цвета, обои и баннер

Всё настраивается CSS-переменными. Свои значения ставьте в «Внешнем виде сайта» **после** строк `@import` — либо правьте блок «Палитра» из `site.css`, либо добавьте ещё один такой же блок (как в примере ниже). Он должен идти позже: тогда ваши значения перебьют тему.

Цвета пишутся тремя числами `R, G, B` через запятую, без `rgb()`. Остальные оттенки (кнопки, ник, меню, наведение) тема считает сама: достаточно поменять `--accent`.

Обёртку `@media screen and (min-width: 1px) { html:root { … } }` не удаляйте, иначе Шикимори применит стиль только на экранах шире 1024px.

### Акцент

| Переменная | Что меняет | По умолчанию |
| --- | --- | --- |
| `--accent` | главный цвет: ссылки, кнопки, ник, подсветка, активные вкладки | `232, 108, 108` |
| `--link` | только ссылки; можно задать отдельно от акцента | как `--accent` |

### Фон и баннер

| Переменная | Что меняет | По умолчанию |
| --- | --- | --- |
| `--bg-image` / `--bg-image-mobile` | обои на ПК / на телефоне, `url("…")` | обои темы |
| `--bg-color` / `--bg-color-mobile` | цвет под обоями, пока они грузятся | средний тон обоев |
| `--bg-dim` | затемнение обоев, от 0 до 1 | `.5` |
| `--bg-blur` / `--bg-blur-mobile` | размытие обоев на ПК / на телефоне | `0px` / `1.5px` |
| `--bg-zoom` | приближение обоев на ПК, `1` — без зума | `1.08` |
| `--profile-banner` | баннер над профилем, `url("…")` | нет (в `site.css` можно подставить свою картинку) |
| `--profile-banner-height` | высота баннера на ПК | `300px` |
| `--profile-banner-height-mobile` | высота баннера на телефоне | `170px` |
| `--profile-banner-position` | какую часть картинки показывать: `center`, `top` или, например, `50% 30%` | `center` |
| `--profile-banner-glow` | свечение под баннером, `0` — выключить | `.5` |

### Стекло и текст

| Переменная | Что меняет | По умолчанию |
| --- | --- | --- |
| `--glass` | цвет стеклянных блоков, меню и окон | `30, 34, 42` |
| `--glass-light` | рамки и блики на стекле | `255, 255, 255` |
| `--glass-blur` | размытие под стеклом (Chrome, Firefox; на телефоне и у стрелок лент) | `5px` |
| `--text` | основной текст | `236, 240, 247` |
| `--text-2` | подписи, второстепенный текст | `170, 178, 192` |
| `--text-3` | даты, счётчики | `140, 148, 160` |
| `--text-strong` | заголовки карточек и текст на кнопках | `255, 255, 255` |

Полный список с пояснениями, включая оценки и шкалы, — в комментариях [`site.css`](site.css).

### Пример: синий акцент и другие обои

Этот блок вставьте **после** строк `@import`. Скриншоты выше — тема по умолчанию (алый акцент и стандартные обои). Ниже та же страница: слева как есть, справа — после этого примера.

```css
@media screen and (min-width: 1px) {
  html:root {
    /* синий акцент: кнопки, ник, ссылки и подсветка перекрасятся сами */
    --accent: 90, 155, 255;
    --link: var(--accent);

    /* другие обои (ссылка без символа @) */
    --bg-image: url("//cdn.jsdelivr.net/gh/Hikisey/shikimori-theme/bg_blue.webp");
    --bg-image-mobile: url("//cdn.jsdelivr.net/gh/Hikisey/shikimori-theme/bg_blue_m.webp");
    --bg-color: 33, 58, 84;
    --bg-color-mobile: 39, 61, 87;
    --bg-dim: .35;
    --bg-blur: 3px;

    /* синеватое стекло, размытие чуть сильнее */
    --glass: 22, 32, 54;
    --glass-blur: 8px;

    --text: 236, 240, 247;
    --text-2: 170, 178, 192;
  }
}
```

![Сравнение: тема по умолчанию и пример с синим акцентом](docs/compare.jpg)

В ссылках на картинки не должно быть символа `@`: Шикимори его вырезает. Обои из примера — [Kanchenjunga South Peak](https://commons.wikimedia.org/wiki/File:Kanchenjunga_South_Peak_%28Unsplash%29.jpg) (Mukesh Jain, Unsplash, CC0), файлы `bg_blue.webp` и `bg_blue_m.webp` лежат в репозитории.

## Для разработчиков

Устройство темы, сборка и правила правок — в [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) и [AGENTS.md](AGENTS.md).
