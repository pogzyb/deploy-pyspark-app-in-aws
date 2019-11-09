# ml/regressor.py
from pandas import DataFrame
from numpy import expm1
from typing import Dict, List
from concurrent.futures import ProcessPoolExecutor
from aiohttp.web import Application
import asyncio
import dill
import signal
import logging
import os

logger = logging.getLogger(__name__)
_pipeline = None


async def init_workers(app: Application, pipeline_path: str) -> ProcessPoolExecutor:

    num_workers = int(os.getenv('NUM_PROC_WORKERS', 2))
    dr = DurationRegressor()
    executor = ProcessPoolExecutor(max_workers=num_workers)
    loop = asyncio.get_event_loop()

    fs = [loop.run_in_executor(executor, dr.load, pipeline_path) for i in range(0, num_workers)]
    await asyncio.gather(*fs)

    async def close_executor(app: Application) -> None:
        fs = [loop.run_in_executor(executor, dr.clean_up) for i in range(0, num_workers)]
        await asyncio.shield(asyncio.gather(*fs))
        executor.shutdown(wait=True)

    app.on_cleanup.append(close_executor)
    app['executor'] = executor
    logger.info(f'Started [{num_workers}] worker processes!')
    return executor


class DurationRegressor(object):

    def __init__(self, pipeline_file=None):
        self._pipeline_file = pipeline_file

    @staticmethod
    def load(pipeline_full_path) -> None:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        global _pipeline
        if not _pipeline:
            dill._dill._reverse_typemap['ClassType'] = type
            _pipeline = dill.load(open(pipeline_full_path, 'rb'))
            logger.info(f'Loaded Pipeline Object')
        return

    @staticmethod
    def clean_up() -> None:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        global _pipeline
        _pipeline = None
        logger.info(f'Cleaned up Pipeline Object.')

    def get_duration(self, data: Dict[str, List[str]]) -> float:
        if not _pipeline:
            logger.info(f'Loading Pipeline Object.')
            self.load(self._pipeline_file)
        if not _pipeline:
            raise RuntimeError('Pipeline Object was not loaded.')
        df = DataFrame(data)
        pred = _pipeline.predict(df)
        duration_in_minutes = round(expm1(pred[0]) / 60, 2)
        return duration_in_minutes
