# ScheduleSync
Экспортирует расписание с [сайта университета](http://oreluniver.ru/schedule) в Календарь Google Calendar или в ics-файл.

## Что нужно знать заранее

ЧТобы запустить любой скрипт, понадобится идентификатор группы или преподавателя. Как его получить (Google Chrome):

1. Найти свое расписание на [сайте](http://oreluniver.ru/schedule), прокликав по всем пунктам, например (Студент, ИПАИТ, 1 курс, 180-СГ)
2. Нажать `F12`
3. На панели разработчика выбрать вкладку `Application`
4. Пункт `Cookies`
5. В таблице смотрим:
    - Для преподавателей: `prep`
    - Для студентов: `group`

## Schedule-Export
Чтобы запустить утилиту из командной строки (`Unix`), набрать:
```bash
$ python schedulesync-export.py -id XX
```

Если больше ничего не указывать, скрипт попытается экспортировать расписание студента на неделю в файл `schedule.ics`

Если нужно расписание преподавателя, то в конце строки необходимо добавить параметр `-p` или `--person`:
```bash
$ python schedulesync-export.py -id 3135 -p
```

### Дополнительные параметры запуска
- `-f` или `--filename` указывает, в какой файл сохранять данные (файл перезаписывается или создается), расширение желательно указывать (по умолчанию `schedule.ics`)
```
$ python schedulesync-export.py -id 3135 -p -f 'schedule-61PG.ics'
```
- `-w` или `--weeks` - количество недель вперед, на которые необходимо получить расписание (по умолчанию только текущая)
```
$ python schedulesync-export.py -id 3135 -p -f 'schedule-61PG.ics' -w 10
```
## ScheduleSync-Google

Позволяет добавить расписание ваших занятий в Google Календарь. Чтобы это сделать средствами скрипта, первый раз придется проделать следующую процедуру:
* Дать доступ скрипту к аккаунту Google
    1. Зарегистрировать собственное приложение на Google Cloud Platform
    2. Для этого приложения создать ключ OAuth (искать по фразам: google client secret)
    3. Около ключа есть кнопка "Скачать"
    4. Переименовать полученный ключ в client_secret.json
* Дать доступ к календарю
    5. В учетной записи Google создать новый календарь:
        - перейти в (https://calendar.google.com/)[календарь]
        - слева "Мои календари" нажать на стрелку
        - Создать новый календарь
    6. Получить идентификатор созданного календаря:
        - в списке календарей выбрать только что созданный
        - нажать на стрелку меню
        - выбрать "Настройки календаря"
        - на открывшейся вкладке найти пункт "Адрес календаря"
        - сохранить себе идентификатор календаря (пример: "40979...0gld2tao4@group.calendar.google.com"
* Запустить скрипт
```bash
$ python schedulesync-google.py -id XX -c 40979...0gld2tao4@group.calendar.google.com
```

Если скрипт запускается первый раз, то в браузере откроектся окно, где ваше созданное приложение запросит доступ к календарям, нужно одобрить. После этого, если идентификатор и ссылка на календарь верны, в календаре появятся новые события.

### Параметры запуска
- `-c` или `--calendar` - адрес календаря, в который выгружается расписание **(обязательный параметр)**
- `-p` или `--person` - указывает, что должно быть загружено расписание преподавателя
```
$ python schedulesync-google.py -id 3135 -c 40979...0gld2tao4@group.calendar.google.com -p
```
- `-w` или `--weeks` - количество недель вперед, на которые необходимо получить расписание (по умолчанию только текущая)
```
$ python schedulesync-google.py -id 3135 -c 40979...0gld2tao4@group.calendar.google.com -p -w 10
```

>***Примечание: *** Параметр `-f` или `--filename` здесь не работает.

## Tips
Before usage should be generated OAuth client secret file [here](https://console.developers.google.com/apis/credentials). Algorithm of generating OAuth client secret is similar to [this one](https://github.com/burnash/gspread/wiki/How-to-get-OAuth-access-token-in-console%3F). 

There is an issue with permissions for "cacerts.txt" (part of httplib2 library) in OS X. Could be fixed as described [here](http://stackoverflow.com/questions/15696526/ssl-throwing-error-185090050-while-authentication-via-oauth).