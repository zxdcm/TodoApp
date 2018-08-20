from lib.exceptions import TimeError
from datetime import datetime as dt


def validate_task_dates(start_date, end_date):
    if start_date and end_date:
        if start_date >= end_date:
            raise TimeError(f'Start date has to be less than end date')


def validate_plan_end_date(end_date):
    if end_date < dt.now():
        raise TimeError(
            f'Plan end date has to be greater than {dt.now():%Y-%m-%d %H:%M}')


def enum_converter(value, type, ex, mes):
    try:
        value = type[value.upper()]
    except KeyError as e:
        raise ex(mes) from e
    return value
