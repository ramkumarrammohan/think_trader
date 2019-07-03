import peewee
import datetime
from .script import Script
from db.database import BaseModel


class Ticker5min(BaseModel):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    script_id = peewee.ForeignKeyField(Script, backref='script')
    # Note: combined unique between 'record_datetime' & 'script_id is available
    record_datetime = peewee.DateTimeField()
    open_price = peewee.FloatField()
    high_price = peewee.FloatField()
    low_price = peewee.FloatField()
    close_price = peewee.FloatField()
    volume = peewee.BigIntegerField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(Ticker5min, self).save(*args, **kwargs)

    class Meta:
        table_name = "ticker_5min"
        indexes = (
            (('script_id', 'record_datetime'), True),
        )
