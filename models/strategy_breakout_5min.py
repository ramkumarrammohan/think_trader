import peewee
import datetime
from .script import Script
from db.database import BaseModel


class StrategyBreakout_5Min(BaseModel):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    script_id = peewee.ForeignKeyField(Script, backref='script', unique=True)

    order_type = peewee.FixedCharField(max_length=5)  # LONG / SHORT
    date = peewee.DateField()
    upper_cutoff_price = peewee.FloatField()
    lower_cutoff_price = peewee.FloatField()
    entry_price = peewee.FloatField()
    entry_time = peewee.DateTimeField()
    max_negative_price_after_entry = peewee.FloatField()
    max_positive_price_after_entry = peewee.FloatField()
    max_negative_percent = peewee.FloatField()
    max_positive_percent = peewee.FloatField()
    transit_time_for_one_percent_gain = peewee.TimeField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(StrategyBreakout_5Min, self).save(*args, **kwargs)

    class Meta:
        table_name = "strategy_breakout_5min"
        indexes = (
            (('script_id', 'date', 'order_type'), True),
        )
