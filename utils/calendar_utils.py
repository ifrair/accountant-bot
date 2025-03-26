import logging
import os
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from zoneinfo import ZoneInfo

from .json_utils import push_to_json, take_from_json
from .utils import is_int


def get_datetime_string(dt_json):
    date_string = f"{str(dt_json['year']).zfill(4)}.{str(dt_json['month']).zfill(2)}.{str(dt_json['day']).zfill(2)}"
    time_string = f"{str(dt_json['hour']).zfill(2)}:{str(dt_json['minute']).zfill(2)}"
    return date_string + ' ' + time_string


# gets date of last interaction with recount function
def get_datetime_from_json(timezone, date_json):
    date = datetime(
        date_json["year"],
        date_json["month"],
        date_json["day"],
        date_json["hour"],
        date_json["minute"],
        date_json["second"],
        tzinfo=ZoneInfo(timezone)).isoformat()
    return date


# updates last interaction date with recount
def last_date_update(date_now):
    date_of_last_recount = take_from_json("last_time")
    date_of_last_recount["year"] = date_now.year
    date_of_last_recount["month"] = date_now.month
    date_of_last_recount["day"] = date_now.day
    date_of_last_recount["hour"] = date_now.hour
    date_of_last_recount["minute"] = date_now.minute
    date_of_last_recount["second"] = date_now.second
    push_to_json("last_time", date_of_last_recount)


# gets services of Google calendar
def connect_to_calendar():
    url = ['https://www.googleapis.com/auth/calendar.readonly']

    config_json = take_from_json("config")
    creds = None
    if os.path.exists(config_json["google_token"]):
        creds = Credentials.from_authorized_user_file(
            config_json["google_token"], url)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            config_json["credentials"], url)
        creds = flow.run_local_server(
            port=0, access_type='offline', prompt='consent')
        creds_to_json = creds.to_json()
        push_to_json("google_token", creds_to_json, True)
    service = build('calendar', 'v3', credentials=creds)
    return service


# processes the event and return errors (if they exist)
def processing_event(event, need_push_json=True):
    money_counts = take_from_json("money_count")
    event_start = event['start'].get('dateTime', event['start'].get('date'))
    summary = event.get('summary', 'Нет названия')
    description = event.get('description', 'Нет описания')
    if summary == "Нет названия":
        return '', '', 0, 0

    error_text = (f"НЕПРАВИЛЬНЫЙ ФОРМАТ ОПИСАНИЯ!\n"
                  f"Событие: {summary}\n"
                  f"Дата занятия: {event_start}\n"
                  f"Описание: {description}\n\n")
    summary_list = list(summary.split())
    description_list = list(description.split())

    if ("урок" in summary_list) or ("Урок" in summary_list):
        people = [(summary_list[0], description_list[0])]
    elif ("Группа" in summary_list) or ("группа" in summary_list):
        people = [(description_list[i], description_list[i+1]) for i in range(0, len(description_list) - 1, 2)]
    else:
        return '', '', 0, 0

    money_sum = 0
    event_text = summary + ': '

    for name, money_count in people:
        if not is_int(money_count):
            logging.error(error_text)
            return '', error_text, 0, 0

        money_count = abs(int(money_count))
        money_sum += money_count

        if name not in money_counts:
            money_counts[name] = 0
        money_counts[name] -= money_count
        event_text += f'{name}-{money_count}, '

    event_text = event_text[:-2] + '\n'
    if need_push_json:
        push_to_json("money_count", money_counts)

    event_end = event['end'].get('dateTime', event['end'].get('date'))
    start_dt = datetime.fromisoformat(event_start)
    end_dt = datetime.fromisoformat(event_end)
    hours_sum = (end_dt - start_dt).total_seconds() / 60 / 60

    return event_text, '', money_sum, hours_sum


def get_from_to_now_datetime(from_time_json):
    config_json = take_from_json("config")
    timezone = config_json['timezone']
    date_now = datetime.now(ZoneInfo(timezone)).replace(microsecond=0)
    from_date = get_datetime_from_json(timezone, from_time_json)
    to_date = date_now.isoformat()
    return from_date, to_date, date_now


def get_events_by_time(service, from_time, to_time):
    config_json = take_from_json("config")
    events_result = service.events().list(
        calendarId=config_json["calendar_id"],
        timeMin=from_time,
        timeMax=to_time,
        timeZone=config_json['timezone'],
        singleEvents=True,
        orderBy='startTime').execute()
    return events_result.get('items', [])


# recounting from last time
def recount_money():
    # recounts time moments to request
    from_date, to_date, date_now = get_from_to_now_datetime(take_from_json("last_time"))

    service = connect_to_calendar()
    events = get_events_by_time(service, from_date, to_date)
    if not events:
        logging.info('Нет предстоящих событий.\n\n')
    last_date_update(date_now)

    events_text = ''
    errors_text = ''
    money_sum = 0
    hours_sum = 0
    for event in events:
        processed = processing_event(event)
        events_text += processed[0]
        errors_text += processed[1]
        money_sum += processed[2]
        hours_sum += processed[3]
    return events_text, errors_text, money_sum, hours_sum
