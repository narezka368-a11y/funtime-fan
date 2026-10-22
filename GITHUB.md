# Как выложить сайт на GitHub Pages

Сайт статический: `index.html` в корне — это уже готовый сайт. Пути к картинкам
относительные, поэтому он нормально работает и в подпапке `username.github.io/repo/`.

Два способа: без установки программ (через сайт GitHub) и одной командой (через `gh`).

---

## Способ 1. Через сайт GitHub (ничего устанавливать не нужно)

1. Зарегистрируйся на [github.com](https://github.com) (бесплатно).
2. Нажми **New repository**: имя `funtime-fan-site`, видимость **Public**, без README.
3. На странице репозитория — **Add file → Upload files**. Перетащи туда содержимое
   этой папки: `index.html`, `css`, `js`, `assets`, `README.md`, а `tools/` можно не
   тащить (это генераторы графики, для сайта они не нужны).
4. Внизу нажми **Commit changes**.
5. **Settings → Pages**:
   - *Source*: `Deploy from a branch`
   - *Branch*: `main`, папка `/ (root)`
   - **Save**
6. Через 1–2 минуты сайт откроется по адресу:

   ```
   https://ТВОЙ_НИК.github.io/funtime-fan-site/
   ```

Переименовать репозиторий можно в **Settings → General → Repository name** —
адрес изменится вместе с именем.

---

## Способ 2. Скриптом (если есть git и gh)

Установка инструментов (PowerShell, один раз):

```powershell
winget install --id Git.Git -e
winget install --id GitHub.cli -e
gh auth login          # вход через браузер
```

Дальше из папки сайта:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy.ps1
# или, если стоит PowerShell 7:
pwsh -File .\deploy.ps1 -RepoName "funtime"
```

Скрипт сам: проверит вход в GitHub, создаст локальный репозиторий, закоммитит,
создаст публичный репозиторий на GitHub, запушит и включит Pages в корне ветки `main`.
В конце напечатает адрес сайта.

Скрипт проверен на разбор синтаксиса (PowerShell 5.1 + UTF-8 BOM), но на этой машине
нет ни `git`, ни `gh`, поэтому полный прогон не выполнялся. Если он где-то упрётся —
делай способом 1, он без установки программ.

---

## Свой домен (по желанию)

1. Купи домен (например `funtime-fan.ru` у reg.ru или timeweb) — 200–900 ₽/год.
2. В **Settings → Pages → Custom domain** впиши домен.
3. У регистратора добавь CNAME-запись: `www` → `ТВОЙ_НИК.github.io`,
   и A-записи на `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
4. Включи галочку **Enforce HTTPS** (сертификат выпустится сам, до 24 часов).

---

## Обновление сайта

Поменял текст в `index.html` → на GitHub: **Add file → Upload files** тем же файлом →
Commit. Pages пересоберётся сам за минуту.

Или локально:

```powershell
git add -A
git commit -m "правки текста"
git push
```
