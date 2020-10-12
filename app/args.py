import argparse

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    "--host", type=str, default="0.0.0.0", help="указание хоста"
)
parser.add_argument("--port", type=int, default=8000, help="указание порта")
parser.add_argument(
    "--emojis",
    nargs="+",
    default=[":smile:", ":snake:"],
    help="указание эмоджи, список смотреть тут https://www.webfx.com/tools/emoji-cheat-sheet/",
)
parser.add_argument(
    "--timeout",
    type=int,
    default=5 * 60,
    help="таймаут до выдачи пустоты в секундах",
)

args = parser.parse_args()
