import peewee
import datetime
from .script import Script
from db.database import BaseModel


class ScriptInfo(BaseModel):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    script_id = peewee.ForeignKeyField(Script, backref='script', unique=True)
    volume = peewee.IntegerField()
    ltp = peewee.FloatField()
    day_low = peewee.FloatField()
    day_high = peewee.FloatField()
    day_open = peewee.FloatField()
    day_close = peewee.FloatField()
    low_52 = peewee.FloatField()
    high_52 = peewee.FloatField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(ScriptInfo, self).save(*args, **kwargs)

    class Meta:
        table_name = "script_info"
