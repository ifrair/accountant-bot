import logging
import os
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from util import is_int, push_to_json, take_from_json


def get_datetime_string(dt_json):
    date_string = f"{dt_json['year']}.{dt_json['month']}.{dt_json['day']}"
    time_string = f"{dt_json['hour']}:{dt_json['minute']}"
    return date_string + ' ' + time_string

# gets date of last interaction with recount function
def get_last_date_time():
    config_json = take_from_json("config.json")
    date_of_last_recount = take_from_json(config_json["last_time"])
    date = datetime(
        date_of_last_recount["year"],
        date_of_last_recount["month"],
        date_of_last_recount["day"],
        date_of_last_recount["hour"],
        date_of_last_recount["minute"],
        date_of_last_recount["second"]).isoformat() + 'Z'
    return date


# gets date from datetime.now()
def get_now_date():
    date_now = datetime.now()
    date = datetime(
        date_now.year,
        date_now.month,
        date_now.day,
        date_now.hour,
        date_now.minute,
        date_now.second).isoformat() + 'Z'
    return date


# updates last interaction date with recount
def last_date_update(date_now):
    config_json = take_from_json("config.json")
    date_of_last_recount = take_from_json(config_json["last_time"])
    date_of_last_recount["year"] = date_now.year
    date_of_last_recount["month"] = date_now.month
    date_of_last_recount["day"] = date_now.day
    date_of_last_recount["hour"] = date_now.hour
    date_of_last_recount["minute"] = date_now.minute
    date_of_last_recount["second"] = date_now.second
    push_to_json(config_json["last_time"], date_of_last_recount)


# gets services of Google calendar
def get_service():
    url = ['https://www.googleapis.com/auth/calendar.readonly']

    config_json = take_from_json("config.json")
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
        push_to_json(config_json["google_token"], creds_to_json, True)
    service = build('calendar', 'v3', credentials=creds)
    return service


# processes the event and return errors (if they exist)
def processing_event(event):
    config_json = take_from_json("config.json")
    money_counts = take_from_json(config_json["money_count"])
    event_start = event['start'].get('dateTime', event['start'].get('date'))
    summary = event.get('summary', 'Нет названия')
    description = event.get('description', 'Нет описания')
    if summary == "Нет названия":
        return '', ''

    error_text = f"""НЕПРАВИЛЬНЫЙ ФОРМАТ ОПИСАНИЯ!
    {summary};
    Дата занятия: {event_start};
    Описание - {description}\n"""
    summary_list = list(summary.split())
    description_list = list(description.split())

    if ("урок" in summary_list) or ("Урок" in summary_list):
        money = description_list[0]
        people = [(summary_list[0], money)]
    elif ("Группа" in summary_list) or ("группа" in summary_list):
        people = [(description_list[i], description_list[i+1]) for i in range(0, len(description_list) - 1, 2)]

    else:
        return '', ''

    event_text = summary + ': '
    for name, money_count in people:
        if not is_int(money_count):
            logging.error(error_text)
            return '', error_text
        money_count = abs(int(money_count))
        if name not in money_counts:
            money_counts[name] = 0
        money_counts[name] -= money_count
        event_text += f'{name}-{money_count}, '
    event_text = event_text[:-2] + '\n'
    push_to_json(config_json["money_count"], money_counts)
    return event_text, ''


def recount():
    config_json = take_from_json("config.json")
    service = get_service()

    date_now = datetime.now()
    from_date = get_last_date_time()
    to_date = get_now_date()
    last_date_update(date_now)

    events_result = service.events().list(
        calendarId=config_json["calendar_id"],
        timeMin=from_date,
        timeMax=to_date,
        singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])
    events_text = ''
    errors_text = ''
    if not events:
        logging.info('Нет предстоящих событий.\n\n')
    for event in events:
        processed = processing_event(event)
        events_text += processed[0]
        errors_text += processed[1]
    return events_text, errors_text
