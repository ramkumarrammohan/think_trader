from datetime import datetime, timedelta

ALPHA_API_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y %b %d'
TIME_FORMAT = '%H:%M:%S'
DATE_TIME_FORMAT = '{} {}'.format(
    DATE_FORMAT, TIME_FORMAT)  # Ex: 2019 Jun 26 03:25:00


def ist_from_uscentral(dt):
    time_delta = timedelta(hours=9, minutes=30)
    ist_dt = datetime.strptime(dt, ALPHA_API_DATE_TIME_FORMAT)
    return ist_dt + time_delta


def is_weekday(dt):
    return dt.isoweekday() < 6
