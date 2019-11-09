# app/__init__.py
from app.handler import AppHandler
from ml.regressor import init_workers
from db.models import init_database
from aiohttp.web import Application
import aiohttp_jinja2
import jinja2
import logging
import os


logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.INFO)
basedir = os.path.abspath(os.path.dirname(__file__))


async def create_app() -> Application:
    app = Application()

    pipeline_file = os.getenv('PIPELINE_ABSPATH')
    stations_csv = os.getenv('STATIONS_ABSPATH')

    AppHandler(app, pipeline_path=pipeline_file)

    await init_workers(app, pipeline_path=pipeline_file)
    await init_database(app, csv_file=stations_csv)

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(basedir, 'templates')))

    return app
