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

## Установка библиотек

Для запуска скрипта используется Python 2.7. Библиотеки, используемые в скрипте, по умолчанию отсутствуют, поэтому их надо установить.

- Первым делом нужно установить pip, запустив `pip.py`:
`sudo python pip.py`
- Затем устанавливаются отсутствующие библиотеки:
```
pip install httplib2
pip install oauth2client
pip install --upgrade google-api-tython-client
```

## Schedule-Export
Чтобы запустить утилиту из командной строки (`Unix`), набрать:
```bash
$ python schedulesync-export.py -id XX
```

Если больше ничего не указывать, скрипт попытается экспортировать расписание студента на неделю в файл `schedule.ics`

Если нужно расписание преподавателя, то в конце строки необходимо добавить параметр `-t` или `--terson`:
```bash
$ python schedulesync-export.py -id 3135 -t
```

### Дополнительные параметры запуска
- `-f` или `--filename` указывает, в какой файл сохранять данные (файл перезаписывается или создается), расширение желательно указывать (по умолчанию `schedule.ics`)
```
$ python schedulesync-export.py -id 3135 -t -f 'schedule-61PG.ics'
```
- `-w` или `--weeks` - количество недель вперед, на которые необходимо получить расписание (по умолчанию только текущая)
```
$ python schedulesync-export.py -id 3135 -t -f 'schedule-61PG.ics' -w 10
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
        - перейти в [календарь](https://calendar.google.com/)
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
- `-t` или `--teacher` - указывает, что должно быть загружено расписание преподавателя
```
$ python schedulesync-google.py -id 3135 -c 40979...0gld2tao4@group.calendar.google.com -t
```
- `-w` или `--weeks` - количество недель вперед, на которые необходимо получить расписание (по умолчанию только текущая)
```
$ python schedulesync-google.py -id 3135 -c 40979...0gld2tao4@group.calendar.google.com -t -w 10
```
- `-e` или `--extended` - расширенный заголовок для события, по умолчанию `False` устанавливает заголовок следующего вида **"НП (пр) Фамилия И. О."**, `--extended` создает заголовок вида **"Название предмета целиком (лек)"**
```
$ python schedulesync-google.py -id 3135 -c 40979...0gld2tao4@group.calendar.google.com -t -w 10 -e
```

- `-d` или `--different` - запрещает объединять события для подгрупп, предполагая, что занятия происходят в разных аудиториях
```
$ python schedulesync-google.py -id 3135 -c 40979...0gld2tao4@group.calendar.google.com -t -w 10 -d
```

>**Примечание:** Параметр `-f` или `--filename` здесь не работает.

## Замеченные проблемы

- При экспорте данных в ics и последующем импорте в Google Календарь, может быть сообщено, что получено 15 событий, а успешно обработано только 10 - эта ситуация связана с подгруппами: два события для подгрупп имеют почти одинаковые данные и поэтому одно не обрабатывается.

## Tips
Before usage should be generated OAuth client secret file [here](https://console.developers.google.com/apis/credentials). Algorithm of generating OAuth client secret is similar to [this one](https://github.com/burnash/gspread/wiki/How-to-get-OAuth-access-token-in-console%3F). 

There is an issue with permissions for "cacerts.txt" (part of httplib2 library) in OS X. Could be fixed as described [here](http://stackoverflow.com/questions/15696526/ssl-throwing-error-185090050-while-authentication-via-oauth).