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
    date_string = f"{dt_json['year']}.{dt_json['month']}.{dt_json['day']}"
    time_string = f"{dt_json['hour']}:{dt_json['minute']}"
    return date_string + ' ' + time_string


# gets date of last interaction with recount function
def get_last_date_time(timezone):
    date_of_last_recount = take_from_json("last_time")
    date = datetime(
        date_of_last_recount["year"],
        date_of_last_recount["month"],
        date_of_last_recount["day"],
        date_of_last_recount["hour"],
        date_of_last_recount["minute"],
        date_of_last_recount["second"],
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
def get_service():
    url = ['https://www.googleapis.com/auth/calendar.readonly']

    config_json = take_from_json("config")
    creds = None
    if os.path.exists(config_json["google_token"]):
        creds = Credentials.from_authorized_user_file(
            config_json["google_token"], url)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config_json["credentials"], url)
            creds = flow.run_local_server(
                port=0, access_type='offline', prompt='consent')
        creds_to_json = creds.to_json()
        push_to_json("google_token", creds_to_json, True)
    service = build('calendar', 'v3', credentials=creds)
    return service


# processes the event and return errors (if they exist)
def processing_event(event):
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
    push_to_json("money_count", money_counts)

    event_end = event['end'].get('dateTime', event['end'].get('date'))
    start_dt = datetime.fromisoformat(event_start)
    end_dt = datetime.fromisoformat(event_end)
    hours_sum = (end_dt - start_dt).total_seconds() / 60 / 60
    return event_text, '', money_sum, hours_sum


def recount_money():
    config_json = take_from_json("config")
    service = get_service()

    timezone = config_json['timezone']
    date_now = datetime.now(ZoneInfo(timezone)).replace(microsecond=0)
    from_date = get_last_date_time(timezone)
    to_date = date_now.isoformat()
    last_date_update(date_now)

    events_result = service.events().list(
        calendarId=config_json["calendar_id"],
        timeMin=from_date,
        timeMax=to_date,
        timeZone=timezone,
        singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])
    if not events:
        logging.info('Нет предстоящих событий.\n\n')
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
