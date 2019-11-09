# app/utils.py
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def prepare_form_data(form_data: dict) -> dict:
    member_map = {'on': 'Member', 'off': 'Casual'}
    station_num = int(form_data.get('station-num'))
    clean_form_data = {
        'Start date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'Member type': [member_map[form_data.get('membership')]],
        'Start station number': [station_num],
    }
    return clean_form_data
