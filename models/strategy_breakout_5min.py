import peewee
import datetime
from .script import Script
from db.database import BaseModel


class StrategyBreakout_5Min(BaseModel):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    script_id = peewee.ForeignKeyField(Script, backref='script', unique=True)
    date = peewee.DateField()
    # entry criteria
    upper_cutoff_price = peewee.FloatField()
    lower_cutoff_price = peewee.FloatField()
    # buy prop
    buy = peewee.BooleanField()
    buy_entry_time = peewee.TimeField(null=True)
    max_positive_after_buy_entry = peewee.FloatField()
    max_negative_after_buy_entry = peewee.FloatField()
    time_to_reach_one_percent_after_buy = peewee.TimeField(null=True)
    # sell prop
    sell = peewee.BooleanField()
    sell_entry_time = peewee.DateTimeField(null=True)
    max_positive_after_sell_entry = peewee.FloatField()
    max_negative_after_sell_entry = peewee.FloatField()
    time_to_reach_one_percent_after_sell = peewee.TimeField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(StrategyBreakout_5Min, self).save(*args, **kwargs)

    class Meta:
        table_name = "strategy_breakout_5min"
        indexes = (
            (('script_id', 'date'), True),
        )
