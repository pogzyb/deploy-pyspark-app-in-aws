# db/models.py
from aiohttp.web import Application
from databases import Database
import sqlalchemy as sa
import pandas as pd
import logging
import orm
import os

logger = logging.getLogger(__name__)

database = Database(os.getenv('SQLITE_CONN_URI'))
metadata = sa.MetaData()


async def init_database(app: Application, csv_file: str) -> None:
    engine = sa.create_engine(str(database.url))
    metadata.create_all(engine)
    await populate_stations_table(engine=engine, csv_file=csv_file)

    async def close_database(app: Application) -> None:
        engine.dispose()
        logger.info(f'Closed connection to database!')

    app.on_cleanup.append(close_database)
    logger.info(f'Successfully connected to the database!')
    return


async def populate_stations_table(engine: sa.engine.Engine, csv_file: str) -> None:
    stations_df = pd.read_csv(csv_file, usecols=['TERMINAL_NUMBER', 'LATITUDE', 'LONGITUDE'])
    stations_df.columns = ['station_num', 'station_lat', 'station_long']
    stations_df.to_sql('stations', con=engine, index=True, index_label='id', if_exists='replace')
    logger.info(f'The "stations" table populated from {csv_file}!')
    return


class Station(orm.Model):
    """
    Represents a bikeshare "station"
    """
    __tablename__ = 'stations'
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    station_num = orm.String(max_length=10, unique=True)
    station_lat = orm.Float()
    station_long = orm.Float()

    def __repr__(self):
        return str(self.station_num)

    def __str__(self):
        return str(self.station_num)
