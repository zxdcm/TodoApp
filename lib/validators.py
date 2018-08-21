
from datetime import datetime as dt


def validate_task_dates(start_date, end_date):
    if start_date and end_date:
        if start_date >= end_date:
            raise ValueError(
                f'Task start date has to be less than end date')


def validate_plan_end_date(end_date):
    if end_date < dt.now():
        raise ValueError(
            f'Plan end date has to be greater than {dt.now():%Y-%m-%d %H:%M}')


def validate_reminder_date(date):
    if date < dt.now():
        raise ValueError(
            f'Reminder date has to be greater than {dt.now():%Y-%m-%d %H:%M}')