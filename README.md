# Бот - бухгалтер репетитора
Это русскоязычный телеграм бот - бухгалтер репетитора. Позволяет взаимодействовать с балансами учеников хранимыми в виде .json файлов. 
Также учитывает индимидуальные и групповые уроки из Google календаря репетитора и при пересчете вычитает из балансов учеников нужные суммы.
Поддерживает бэкап с предыдущего пересчета.
Автоматически составляет отчет за различные периоды.
## Для запуска понадобится:
* В папке проекта сделать config.json в следующем формате:
  ```json
  {
    "Token": "ВАШ ТЕЛЕГРАМ ТОКЕН",
    "users": ["ТГ НИКИ ТЕХ КТО БУДЕТ ИМЕТЬ ДОСТУП (БЕЗ @)"],
    "calendar_id": "primary ЛИБО ЕСЛИ БРАТЬ СОБЫТИЯ НЕ ИЗ ГЛАВНОГО КАЛЕНДАРЯ ТО ЕГО ID", 
    "timezone": "Europe/Moscow",
    "money_count": "data/balances.json",
    "last_time": "data/last_time.json",
    "last_time_backup": "data/last_time_backup.json",
    "credentials": "data/credentials.json",
    "google_token": "data/token.json",
    "money_counts_backup": "data/balances_backup.json",
    "logs": "data/logs.txt",
    "start_time": {"year": 2024, "month": 12, "day": 1, "hour": 0, "minute": 0, "second": 0}
    ^ СТАРТОВОЕ ВРЕМЯ ДЛЯ ОТЧЕТА
  }
  ```
* Создать .json файлы (кроме logs и google_token они создаются автоматически при первом запуске) по путям указанным в config<br>
  money_count - база данных ученик-баланс, для начала можно сделать {}<br>
  last_time - дата последнего обновления в формате как start_time можно указать любую начальную дату<br>
  money_counts_backup и last_time_backup - бэкапы, можно скопировать с предыдущих двух<br>
  credentials - этот .json нужно взять на сайте API google calendar
* Подключить библиотеки: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client, aiogram
* При первом запуске понадбится залогиниться в Гугле в браузере
  
