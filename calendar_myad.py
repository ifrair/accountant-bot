import logging
import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from util import push_to_json, take_from_json

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

#gets services of google calendar
def get_service():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    config_json = take_from_json("config.json")
    creds = None
    if os.path.exists(config_json["google_token"]):
        creds = Credentials.from_authorized_user_file(
            config_json["google_token"], SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config_json["credentials"], SCOPES)
            creds = flow.run_local_server(
                port=0, access_type='offline', prompt='consent')
        creds_to_json = creds.to_json()
        push_to_json(config_json["google_token"], creds_to_json, True)
    service = build('calendar', 'v3', credentials=creds)
    return service

# processes the event and return errors (if they exist)
def processing_event(event):
    errors = ''
    config_json = take_from_json("config.json")
    babki_json = take_from_json(config_json["money_count"])
    event_start = event['start'].get('dateTime', event['start'].get('date'))
    summary = event.get('summary', 'Нет названия')
    description = event.get('description', 'Нет описания')
    if summary == "Нет названия":
        return ''
    else:
        summary_list = list(summary.split())
        if ("урок" in summary_list) or ("Урок" in summary_list):
            if not description.isnumeric():
                logging.error(
                    f'НЕПРАВИЛЬНЫЙ ФОРМАТ ОПИСАНИЯ!\n {summary};\n Дата занятия: {event_start};\n Описание - {description}')
                errors += f'НЕПРАВИЛЬНЫЙ ФОРМАТ ОПИСАНИЯ!\n {summary};\n Дата занятия: {event_start};\n Описание - {description}\n\n'
                return errors
            if summary_list[0] not in babki_json:
                babki_json[summary_list[0]] = -int(description)
            else:
                babki_json[summary_list[0]] -= int(description)
        elif ("Группа" in summary_list) or ("группа" in summary_list):
            description_list = list(description.split())
            for i in range(0, len(description_list) - 1, 2):
                if not description_list[i + 1].isnumeric():
                    logging.error(
                        f'НЕПРАВИЛЬНЫЙ ФОРМАТ ОПИСАНИЯ!\n {summary};\n {i};\n Дата занятия: {event_start};\n Описание - {description}\n\n')
                    errors += f'НЕПРАВИЛЬНЫЙ ФОРМАТ ОПИСАНИЯ!\n {summary};\n {i};\n Дата занятия: {event_start};\n Описание - {description}\n\n'
                    return errors
                if description_list[i] not in babki_json:
                    babki_json[description_list[i]] = -int(description_list[i + 1])
                else:
                    babki_json[description_list[i]] -= int(description_list[i + 1])
    push_to_json(config_json["money_count"], babki_json)
    return errors

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
    errors = ''
    if not events:
        logging.info('Нет предстоящих событий.\n\n')
    for event in events:
        processed = processing_event(event)
        errors += processed
    return errors
