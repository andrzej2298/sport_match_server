from dateutil.relativedelta import relativedelta
from datetime import datetime


def get_current_age(birth_date):
    return relativedelta(datetime.now(), birth_date).years
