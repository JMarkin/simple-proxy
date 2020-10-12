# Пример простого http прокси сервера для [lifehacker.ru](https://lifehacker.ru)

Построено на aiohttp, bs4, emojis, esprima

Задача:

1. Простой http прокси  по типу http://localhost:8000 и покажет https://lifehacker.ru
2. Из списка emoji переданного в программу циклически добавлять в конец любого слова из 6 букв.

---

Использование и запуск

```bash
python -m app -h
usage: __main__.py [-h] [--host HOST] [--port PORT]
                   [--emojis EMOJIS [EMOJIS ...]] [--timeout TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           указание хоста (default: 0.0.0.0)
  --port PORT           указание порта (default: 8000)
  --emojis EMOJIS [EMOJIS ...]
                        указание эмоджи, список смотреть тут
                        https://www.webfx.com/tools/emoji-cheat-sheet/
                        (default: [':smile:', ':snake:'])
  --timeout TIMEOUT     таймаут до выдачи пустоты в секундах (default: 300)
```

---
Для запуска локально нужно [poetry](https://python-poetry.org/) удобный пакетный менеджер

Команды для запуска:

1. `poetry install --no-dev`, если нужны либы дял разработки убрать `--no-dev`
2. `poetry run python -m app -h` покажет хелп как выше

---
Можно скачать из релизов собранный бинарник c зависмостями запустить команду `app.dist/app -h`
Собирался с помощью [nuitka](https://github.com/Nuitka/Nuitka)
