# main.py
from aiohttp.web import run_app
from app import create_app
import asyncio
import os


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(create_app())
    run_app(app, host='0.0.0.0', port=os.getenv('APP_PORT'))
