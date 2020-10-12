import json
import emojis as emoji
import esprima


from bs4 import BeautifulSoup
from app.deep_find import gen_dict_extract

blacklist = [
    "[document]",
    "noscript",
    "header",
    "html",
    "meta",
    "head",
    "input",
    "script",
    "style",
]


class AggregateHtml:
    # обработка html файла
    def __init__(self, raw, emojis):
        self.soup = BeautifulSoup(raw.decode("utf-8"), "lxml")
        self._emojis = emojis
        self.remove = []

    def add_emoji(self, match):
        emoj = next(self._emojis)
        return "%s%s" % (match.group(1), emoj)

    def change_str(self, t):
        new_s = []
        for i in t.split():
            emoj = ""
            if len(i) == 6:
                emoj = next(self._emojis)
            new_s.append(f"{i}{emoj}")
        return emoji.encode(" ".join(new_s))

    def change_str_dict(self, d, k):
        d[k] = self.change_str(d[k])

    def aggregate(self):
        # поиск и изменение всех текстовых нод для html
        for t in self.soup.find_all(text=True):
            if str(t) == "\n" or str(t) == " ":
                continue
            if t.parent.name in blacklist:
                continue

            t.parent.append(self.change_str(t))
            self.remove.append(t)
        for t in self.remove:
            t.extract()

        # т.к. сайт построен на nuxtjs внизу хранится объект
        # накста в котором перечислены объекты и данные котоыре потом заполнятся
        script = {}
        txt = None
        for s in self.soup.find_all("script"):
            if s.string and s.string.find("__NUXT__") >= 0:
                # находим скрипт и переводим его в словарик
                script = esprima.toDict(esprima.parseScript(s.string))
                txt = s
                break

        if not txt:
            return

        # заменяем все значнеи котоыре можем найти
        for old, new in gen_dict_extract(
            "value", script, self.change_str_dict
        ):
            if old != new:
                txt.string = txt.string.replace(old, new)


class AggregateJson(AggregateHtml):
    # обработка json-ов
    def __init__(self, raw, emojis):
        self.json = json.loads(raw.decode("utf-8"))
        self._emojis = emojis
        self.remove = []

    def aggregate(self):
        # видос запросов много поэтому тупо прокручиваем все ключи которые известны
        list(gen_dict_extract("title", self.json, self.change_str_dict))
        list(gen_dict_extract("post_title", self.json, self.change_str_dict))
        list(gen_dict_extract("content", self.json, self.change_str_dict))
        list(gen_dict_extract("subtitle", self.json, self.change_str_dict))
