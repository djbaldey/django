# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.utils.dateparse import parse_datetime

# Округление времени:

def round_datetime(value=None, minute=True, hour=False, day=False):
    """
    Округление времени до секунды, минуты, часа или дня.
    По умолчанию до минуты.
        до дня:     rounded(day=True)
        до часа:    rounded(hour=True)
        до минуты:  rounded()
        до секунды: rounded(minute=False)
        
    Если нужно округлить заданное время,то оно передаётся в
    параметре `value`.

    На вход можно подавать как naive, так и aware, результатом будет
    аналогичное.
    Если генерируется новое время, то результатом будет локальное naive
    при settings.USE_TZ = False, иначе - локальное aware.
    """
    if not isinstance(value, timezone.datetime):
        value = timezone.now()

    value = value.replace(microsecond=0)

    if day:
        value = value.replace(hour=0, minute=0, second=0)
    elif hour:
        value = value.replace(minute=0, second=0)
    elif minute:
        value = value.replace(second=0)

    return value

# Получение или преобразование времени в локальную или серверную зоны:

def local_datetime(value=None):
    """
    Переводит значение в текущую зону локального времени или создаёт
    текущее.
    На вход можно подавать как naive, так и aware, результатом будет
    аналогичное, только naive не переводится.
    Если генерируется новое время, то результатом будет naive при
    settings.USE_TZ = False, иначе - aware.
    """
    if not value:
        value = timezone.now()

    if timezone.is_naive(value):
        return value

    return timezone.localtime(value)

def server_datetime(value=None):
    """
    Переводит значение в зону серверного времени или создаёт текущее.
    На вход можно подавать как naive, так и aware, результатом будет
    аналогичное, только naive не переводится.
    Если генерируется новое время, то результатом будет naive при
    settings.USE_TZ = False, иначе - aware.
    """
    if not value:
        value = timezone.now()

    if timezone.is_naive(value):
        return value

    tz_curr = timezone.get_current_timezone()
    tz_serv = timezone.get_default_timezone()

    if tz_curr != tz_serv:
        timezone.activate(tz_serv)
        value = timezone.localtime(value)
        timezone.activate(tz_curr)
    else:
        value = timezone.localtime(value)

    return value

# Принудительные преобразования в локальную или серверную зоны:

def local_datetime_naive(value=None):
    """
    Переводит значение в текущую зону локального времени или создаёт
    текущее.
    Возвращает простое время.
    """
    if timezone.is_naive(value):
        return value
    return timezone.make_naive(local_datetime(value))

def local_datetime_aware(value=None):
    """
    Переводит значение (даже `naive`) в текущую зону локального времени
    или создаёт текущее.
    Возвращает `aware` c текущей временной зоной.
    """
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    return local_datetime(value)

def server_datetime_naive(value=None):
    """
    Переводит значение в зону серверного времени settings.TIME_ZONE.
    Возвращает простое время.
    """
    if timezone.is_naive(value):
        return value
    return timezone.make_naive(server_datetime(value))

def server_datetime_aware(value=None):
    """
    Переводит значение (даже простое) в зону серверного времени.
    Возвращает aware c временной зоной сервера.
    """
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    return server_datetime(value)

# Получение текущего локального или серверного времени:

def local_date():
    """
    Возвращает текущую дату локальной зоны.
    """
    return local_datetime_naive().date()

def local_time():
    """
    Возвращает текущее время локальной зоны.
    """
    return local_datetime_naive().time()

def server_date():
    """
    Возвращает текущую дату сервера по settings.TIME_ZONE.
    """
    return server_datetime_naive().date()

def server_time():
    """
    Возвращает текущее время сервера по settings.TIME_ZONE.
    """
    return server_datetime_naive().time()

# Парсеры с принудительным преобразованием времени в локальную или серверную зоны:

def parse_datetime_to_local_naive(value):
    """
    Парсер строкового значения (naive или aware) в локальное naive.
    """
    value = parse_datetime(value)
    if value:
        return local_datetime_naive(value)
    return None

def parse_datetime_to_local_aware(value):
    """
    Парсер строкового значения (naive или aware) в локальное aware.
    """
    value = parse_datetime(value)
    if value:
        return local_datetime_aware(value)
    return None

def parse_datetime_to_server_naive(value):
    """
    Парсер строкового значения (naive или aware) в серверное naive.
    """
    value = parse_datetime(value)
    if value:
        return server_datetime_naive(value)
    return None

def parse_datetime_to_server_aware(value):
    """
    Парсер строкового значения (naive или aware) в серверное aware.
    """
    value = parse_datetime(value)
    if value:
        return server_datetime_aware(value)
    return None

