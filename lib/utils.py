from dateutil import relativedelta
from .models import EndType


def get_interval(self, period_type, period_quantity):
    if period_type.value == 'hour':
        return relativedelta(hours=period_quantity)
    elif period_type.value == 'day':
        return relativedelta(days=period_quantity)
    elif period_type.value == 'week':
        return relativedelta(weeks=period_quantity)
    elif period_type.value == 'month':
        return relativedelta(months=period_quantity)
    elif period_type.value == 'years':
        return relativedelta(years=period_quantity)


def get_end_type(self, task_start_date,
                 end_date=None, repetitions_amount=None) -> EndType:

    if end_date and repetitions_amount:
        interval = self.get_interval(end_date, repetitions_amount)
        if interval * repetitions_amount + task_start_date < end_date:
            return EndType.AMOUNT
        return EndType.DATE
    '''
        When both end_date and repetitions_amount are set:
            Calculate how much times task can be repeated until the end_date
            if it less then end_date => EndType.AMOUNT
            othwerwise => EndType.DATE
        Otherwise we select EndType by (end_date or repetitions_amount) or
        just EndType.NEVER
    '''

    if end_date:
        return EndType.DATE
    if repetitions_amount:
        return EndType.AMOUNT
    return EndType.NEVER
