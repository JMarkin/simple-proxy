import logging
import sys

from aiohttp import web
from app.app import app, args

logging.root.setLevel(logging.INFO)
logging.root.addHandler(logging.StreamHandler(sys.stdout))

logger = logging.getLogger("proxy")

logger.info(f"Config {args}")

web.run_app(app, port=args.port, host=args.host)
