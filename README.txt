# TODO сделать нормальный README с указанием всех зависимостей, настроек, параметров запуска

#### Сборщик статистики HAProxy ###

Проверялось на версии HAProxy 2.4.23-62cb999, released 2023/06/09

Теоретически, должно работать на всех версиях HAProxy, где имеется выгрузка статистики в JSON


Зависимости:
    requests - для запросов к HAProxy
    pandas - для сохранения данных в xls
    matplotlib - для отрисовки графиков

    Установка: pip3 install requests pandas matplotlib


Файл config.py содержит необходимые переменные:
    - список строк статистики HAProxy, с которых мы будем собирать данные
    - строку подключения к HAProxy

