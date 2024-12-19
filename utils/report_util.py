from datetime import datetime
from zoneinfo import ZoneInfo
from collections import OrderedDict
from .calendar_utils import connect_to_calendar, get_from_to_now_datetime, get_events_by_time, processing_event
from .utils import take_from_json


class Sum:
    def __init__(self, period):
        self.period = period
        self.money = 0
        self.hours = 0
    def add(self, money, hours):
        self.money += money
        self.hours += hours


# makes report about this and prev month, prev 30 days, pre-prev 30 days, prev 4 weeks, all the time
# about sum money, hours, avg hours and avg money
def make_report():
    config_json = take_from_json("config")
    from_date, to_date, now_date = get_from_to_now_datetime(config_json["start_time"])

    service = connect_to_calendar()
    events = get_events_by_time(service, from_date, to_date)
    if not events:
        return "Cобытий не обнаружено"

    sums = OrderedDict([
        ("all", [Sum("Всего")]),
        ("30d", [Sum("За последние 30 дней"), Sum("За 30 дней до этого")]),
        ("mon", [Sum("За этот месяц"), Sum("За прошлый месяц")]),
        ("week", [
            Sum("За эту неделю"),
            Sum("За прошлую неделю"),
            Sum("За позапрошлую неделю"),
            Sum("За позапозапрошлую неделю"),
        ]),
    ])
    first_date = datetime.fromisoformat(from_date)
    for event in events:
        _, _, money, hours = processing_event(event, need_push_json=False)
        sums["all"][0].add(money, hours)

        start_time = datetime.fromisoformat(event["start"]["dateTime"])
        end_time = datetime.fromisoformat(event["end"]["dateTime"])

        day_num_now = (now_date - first_date).days
        day_num = (start_time - first_date).days
        if day_num_now - day_num < 30:
            sums["30d"][0].add(money, hours)
        elif day_num_now - day_num < 60:
            sums["30d"][1].add(money, hours)

        now_year = now_date.year
        now_mon = now_date.month
        previous_month = now_mon - 1 if now_mon > 1 else 12
        previous_year = now_year if now_mon > 1 else now_year - 1
        if end_time.year == now_year and end_time.month == now_mon:
            sums["mon"][0].add(money, hours)
        elif end_time.year == previous_year and end_time.month == previous_month:
            sums["mon"][1].add(money, hours)

        day_of_week = now_date.weekday()
        start_week_day = day_num_now - day_of_week
        for week in range(4):
            if day_num >= start_week_day - week * 7:
                sums["week"][week].add(money, hours)
                break

    rep_text = "На текущий момент:\n\n"
    for sum_list in sums.values():
        for period_sum in sum_list:
            avg = int(period_sum.money/(period_sum.hours if period_sum.hours > 0 else 1))
            rep_text += (f"{period_sum.period}:" + " " * int((25 - len(period_sum.period)) * 2) +
                         f" {period_sum.money} руб, за {round(period_sum.hours, 1)} часов, ~ {avg} руб/ч\n\n")

    return rep_text


def take_balances(money):
    message_text = ''
    for name in sorted(money):
        message_text += (('Долг' if money[name] < 0 else 'Остаток') +
                         f' {name} равен: {money[name]} руб\n')
    return message_text


def take_names(money):
    message_text = ''
    for name in sorted(money):
        message_text += f'`{name}`\n'
    return message_text
