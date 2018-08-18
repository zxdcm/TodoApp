from lib.exceptions import TimeError


def validate_dates(start_date, end_date):
    if start_date and end_date:
        if start_date > end_date:
            raise TimeError(f'Start date has to be less than end date')
