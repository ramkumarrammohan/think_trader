from peewee import Model, MySQLDatabase

db = MySQLDatabase('nse', user='ramkumar', password='password',
                   host='localhost', port=3306)


def database():
    return db


def atomic_insert(MyModel, data):
    with db.atomic():
        for idx in range(0, len(data), 100):
            MyModel.insert_many(data[idx:idx+100]).execute()


class BaseModel(Model):
    class Meta:
        database = db
