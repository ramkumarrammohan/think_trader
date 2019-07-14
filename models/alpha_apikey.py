import peewee
import datetime
from db.database import BaseModel


class AlphaApiKey(BaseModel):
    email = peewee.CharField(unique=True)
    apikey = peewee.CharField(unique=True)
    session_count = peewee.IntegerField()
    day_count = peewee.IntegerField()
    last_used_at = peewee.DateTimeField(
        default=datetime.datetime.now(), null=True)

    class Meta:
        table_name = "alpha_apikey"

    def get_apikey():
        query = (AlphaApiKey.select()
                 .where(AlphaApiKey.day_count < 500)
                 .order_by(AlphaApiKey.session_count.asc(), AlphaApiKey.last_used_at.asc())
                 .limit(2)
                 )
        for obj in query:
            if obj.session_count >= 5:
                time_delta = datetime.datetime.now() - obj.last_used_at
                if time_delta.total_seconds() < 60:
                    continue

            print('id: {}, session_count: {}'.format(obj.id, obj.session_count))
            session_count = obj.session_count + 1
            if (session_count > 5):
                session_count = 1

            update_q = (AlphaApiKey
                        .update({
                            AlphaApiKey.session_count: session_count,
                            AlphaApiKey.day_count: obj.day_count + 1,
                            AlphaApiKey.last_used_at: datetime.datetime.now()})
                        .where(AlphaApiKey.id == obj.id)).execute()
            return (obj.apikey)
