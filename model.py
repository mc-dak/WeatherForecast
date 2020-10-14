from settings import DB_CONFIG, DB_CONFIG_URL
import peewee
from playhouse.db_url import connect, DatabaseProxy
import sys

database_proxy = DatabaseProxy()


class BaseTable(peewee.Model):
    class Meta:
        database = database_proxy


class Weather(BaseTable):
    date = peewee.DateField()
    avgtempC = peewee.CharField()
    windspeedKmph = peewee.CharField()
    weatherDesc = peewee.CharField()
    precipMM = peewee.CharField()
    humidity = peewee.CharField()
    pressure = peewee.CharField()


class Image(BaseTable):
    date = peewee.DateField()
    filename = peewee.CharField()


gettrace = getattr(sys, 'gettrace')

if gettrace():
    database = peewee.SqliteDatabase(DB_CONFIG)
else:
    database = connect(DB_CONFIG_URL)
