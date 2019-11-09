# src/app/handler.py
from aiohttp.web import Application, Response, Request
from dataclasses import dataclass, field
from app.utils import prepare_form_data
from ml.regressor import DurationRegressor
from db.models import Station
from typing import Tuple, Dict, Any
import aiohttp_jinja2
import asyncio
import logging

logger = logging.getLogger(__name__)


def default_stats() -> Dict[str, str]:
    return {'stats': ''}


@dataclass
class AppResponse:
    alert: Tuple[str, str] = ('', '')
    stats: Dict[str, str] = field(default_factory=default_stats)
    duration: float = 0.0
    error: str = ''
    page: str = ''


class AppHandler(object):

    def __init__(self, app, pipeline_path):
        self._init_routes(app)
        self._loop = asyncio.get_event_loop()
        self._dr = DurationRegressor(pipeline_path)

    def _init_routes(self, app: Application) -> None:
        app.router.add_route('GET', '/', self.index, name='index')
        app.router.add_route('POST', '/ride', self.ride, name='ride')
        app.router.add_route('GET', '/info', self.info, name='info')
        app.router.add_route('GET', '/bike_map', self.bike_map, name='bike_map')
        return

    @staticmethod
    def _make_response(**kwargs) -> Dict[str, AppResponse]:
        response = {'payload': AppResponse(**kwargs)}
        return response

    @aiohttp_jinja2.template('index.html')
    async def index(self, request: Request) -> Dict[str, Any]:
        payload = {'page': 'home'}
        response = self._make_response(**payload)
        return response

    @aiohttp_jinja2.template('index.html')
    async def ride(self, request: Request) -> Dict[str, Any]:
        """
        Accepts a POST request containing data from the form
        on the index.html aka "home" page, prepares this data
        to be used as input to the ML pipeline, and finally
        returns the output or predicted "duration" of the ride
        from the ML pipeline.

        :param request: aiohttp request object
        :return: response data as a Dictionary
        """
        form_data = await request.post()
        station_num = str(form_data.get('station-num'))
        station = await Station.objects.get(station_num=station_num)
        if not station:
            message = f'Sorry! Station {station_num} does not exist.'
            logger.info(message)
            payload = {'alert': ('danger', message)}
            error_response = self._make_response(**payload)
            return error_response
        # else:
            # form_data['start_station_lat'] = station.station_lat
            # form_data['start_station_long'] = station.station_long
        prepared_data = prepare_form_data(form_data)
        executor = request.app['executor']
        duration = await self._loop.run_in_executor(
            executor,
            self._dr.get_duration,
            prepared_data
        )
        payload = {
            'duration': duration,
            'page': 'ride prediction'
        }
        success_response = self._make_response(**payload)
        return success_response

    @aiohttp_jinja2.template('info.html')
    async def info(self, request: Request) -> Dict[str, Any]:
        payload = {'page': 'information'}
        response = self._make_response(**payload)
        return response

    @aiohttp_jinja2.template('maps/bike_map.html')
    async def bike_map(self, request: Request) -> Dict[str, Any]:
        payload = {'page': 'home'}
        response = self._make_response(**payload)
        return response
