import json
import logging
import random
import re
import aiohttp

from itertools import cycle
from string import ascii_lowercase
from urllib.parse import urljoin
from aiohttp import web
from aiohttp.client import ClientTimeout

from app.aggregate import AggregateHtml, AggregateJson
from app.args import args

HOST = "lifehacker.ru"
BASE_URL = f"https://{HOST}"

PUBLIC_URL = f"{args.host}:{args.port}"

HOSTS = [
    "auth.lifehacker.ru",
    "fullsearch.lifehacker.ru",
    "pusher.lifehacker.ru",
    "push-stage.lifehacker.ru",
    "push-stage.lifehacker.ru",
    "talker.lifehacker.ru",
]
URLS = {host: "".join(random.choices(ascii_lowercase, k=4)) for host in HOSTS}
_URLS = {val: key for key, val in URLS.items()}

logger = logging.getLogger("proxy")

emojis = args.emojis
emojis = cycle(emojis)


async def proxy(request):
    path = request.match_info["path"]
    target_url = urljoin(BASE_URL, path)
    host = HOST
    for s in _URLS:
        # Изменяем урлы на внешние апишки чтобы избежать cors и обрабатывать апишки
        if path.startswith(s):
            path = path.replace(s, "")
            host = _URLS[s]
            target_url = urljoin(f"https://{host}", path)
            break

    data = await request.read()
    get_data = request.rel_url.query

    # правим хедеры дял запроса
    headers = dict(request.headers)
    headers["Host"] = host
    if "Referer" in headers:
        headers["Referer"] = headers["Referer"].replace(
            f"http://{PUBLIC_URL}", BASE_URL
        )
    headers["Accept-Encoding"] = "identity"

    try:
        async with aiohttp.ClientSession(
            timeout=ClientTimeout(total=args.timeout)
        ) as session:
            if "Upgrade" in request.headers:
                # На пожарник проксируем вебсокет
                ws_c2p = web.WebSocketResponse()
                await ws_c2p.prepare(request)

                async with session.ws_connect(target_url) as ws_p2s:
                    async for msg in ws_c2p:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            if msg.data == "close":
                                await ws_c2p.close()
                            else:
                                ws_p2s.send_str(msg.data)
                                data_p2s = await ws_p2s.receive_str()
                                ws_c2p.send_str(data_p2s)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.info(
                                "ws connection closed with exception %s"
                                % ws_c2p.exception()
                            )
                return ws_c2p
            else:
                async with session.request(
                    request.method,
                    target_url,
                    headers=headers,
                    params=get_data,
                    data=data,
                ) as resp:
                    res = resp
                    raw = await res.read()
    except TimeoutError:
        return web.Response(status=504, text="Timeout Error")

    for url in URLS:
        new_url = f"http://{PUBLIC_URL}/{URLS[url]}"
        raw = raw.replace(
            f"https://{url}".encode("utf-8"),
            new_url.encode("utf-8"),
        )
    raw = raw.replace(BASE_URL.encode("utf-8"), b"")
    raw = re.sub(
        rb"([^\.])(lifehacker\.ru)", rf"\g<1>{PUBLIC_URL}".encode("utf-8"), raw
    )
    raw = raw.replace(b"https", b"http")

    headers = dict(res.headers)

    # прям обязательно только с главного домена, некоторые домены возвращают text/html хотя там json
    if headers.get("Content-Type", "").find("text/html") >= 0 and host == HOST:
        aggr = AggregateHtml(raw, emojis)
        aggr.aggregate()
        raw = str(aggr.soup).encode("utf-8")

    if headers.get("Content-Type", "").find("json") >= 0:
        aggr = AggregateJson(raw, emojis)
        aggr.aggregate()
        raw = json.dumps(aggr.json).encode("utf-8")

    # удаление хедеров чтобы и aiohttp сама вычислила
    if "Transfer-Encoding" in headers:
        del headers["Transfer-Encoding"]
    if "Content-Length" in headers:
        del headers["Content-Length"]

    return web.Response(body=raw, status=res.status, headers=headers)


app = web.Application(client_max_size=1024 ** 3)
app.router.add_route("*", "/{path:.*?}", proxy)
