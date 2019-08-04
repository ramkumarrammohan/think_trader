import peewee
import datetime
from .script import Script
from db.database import BaseModel


class StrategyBreakout_5Min(BaseModel):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    # reference field
    script_id = peewee.ForeignKeyField(Script, backref='script')
    # trading date
    date = peewee.DateField()
    # day max values
    day_max_price = peewee.FloatField()
    day_min_price = peewee.FloatField()
    # entry criteria
    upper_cutoff_price = peewee.FloatField()
    lower_cutoff_price = peewee.FloatField()
    # buy prop
    buy_entry_time = peewee.TimeField(null=True)
    buy_profit_one_percent_time = peewee.TimeField(null=True)
    buy_max_stoploss_before_one_percent = peewee.FloatField(null=True)
    # sell prop
    sell_entry_time = peewee.TimeField(null=True)
    sell_profit_one_percent_time = peewee.TimeField(null=True)
    sell_max_stoploss_before_one_percent = peewee.FloatField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(StrategyBreakout_5Min, self).save(*args, **kwargs)

    class Meta:
        table_name = "strategy_breakout_5min"
        indexes = (
            (('script_id', 'date'), True),
        )
