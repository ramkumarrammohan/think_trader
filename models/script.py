import peewee
import datetime
from db.database import BaseModel


class Script(BaseModel):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    symbol = peewee.CharField(unique=True)
    company_name = peewee.CharField()
    alpha_support = peewee.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(Script, self).save(*args, **kwargs)
