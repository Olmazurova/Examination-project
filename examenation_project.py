#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Программируем дрон для полёта по траектории пятиконечной звезды '''

# Библиотека __future__ нужна для обратной совместимости между python2 и python3
from __future__ import print_function
import math
# Подключаем библиотеку time
import time
# Из библиотеки dronekit подключаем connect для связи с дроном
# Из библиотеки dronekit импортируем VehicleMode для изменения режима полёта дрона
# Из библиотеки dronekit импортируем LocationGlobalRelative для изменения местоположения дрона

from dronekit import connect, VehicleMode, LocationGlobalRelative


# Получение строки подключения
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


# Запускаем SITL если строка соединения не получена
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Подключение к дрону
print('Подключение к дрону: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Запускает моторы дрона и поднимает его на высоту равную aTargetAltitude.
    """

    print("Основные проверки перед запуском")
    # Проверка готовности автопилота перед запуском
    while not vehicle.is_armable:
        print(" Ожидание инициализации дрона...")
        time.sleep(1)

    print("Включение двигателей")
    # Перевод дрона в режим "GUIDED", запуск двигателей
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Проверка запуска двигателей перед взлётом
    while not vehicle.armed:
        print(" Ожидание запуска...")
        time.sleep(1)

    print("Взлёт!")
    vehicle.simple_takeoff(aTargetAltitude)  # Взлёт на заданную высоту

    # Ожидание подъёма дрона на безопасную высоту
    # (иначе полёт будет выполнен немедленно).
    while True:
        print(" Высота: ", vehicle.location.global_relative_frame.alt)
        # Прерывание ожидания и возвращение к основной функции, когда высота набрана на 95%.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Достигнута заданная высота")
            break
        time.sleep(1)


# Запуск дрона и набор высоты
arm_and_takeoff(20)

print("Устанавливаем по умолчанию скорость полёта 10")
vehicle.airspeed = 10

# Координаты точки взлёта и посадки
lat_h = 55.7502372
long_h = 37.6281953

# угол поворота дрона
angle = math.pi / 2  # угол 90 градусов
radius = 0.002 # радиус для широты
coefficient = 111.11 / (111.3 * math.cos(lat_h)) # коэффициент корректировки радиуса для долготы

# Дрон облетает месность по траектории звезды
# Через цикл вычисляем координаты для каждой точки
for i in range(11):
    if i % 2 != 0:
        x = round(long_h - radius * coefficient * 0.4 * math.cos(angle), 6)
        y = round(lat_h + radius * 0.4 * math.sin(angle), 6)
        print(f"Полёт дрона к точке с координатами х: {x}, у: {y} на высоте 25 м.")
        vehicle.simple_goto(LocationGlobalRelative(y, x, 25))
    else:
        y = round(lat_h + radius * math.sin(angle), 6)
        x = round(long_h - radius * coefficient * math.cos(angle), 6)
        print(f"Полёт дрона к точке с координатами х: {x}, у: {y} на высоте 25 м.")
        vehicle.simple_goto(LocationGlobalRelative(y, x, 25))
    angle += math.pi / 5 # если поставить знак минус, то дрон будет лететь против часовой стрелки

    # приостанавливаем программу и смотрим движение дрона на карте
    time.sleep(30)

# Отправляем дрон к точке взлёта
print("Дрон летит к точке взлёта в течение 30 секунд.")
point_home = LocationGlobalRelative(lat_h, long_h, 20)
vehicle.simple_goto(point_home, groundspeed=10)

# приостанавливаем программу и смотрим изменения на карте
time.sleep(30)

print("Посадка дрона")
vehicle.mode = VehicleMode("RTL")

time.sleep(5)

# Отключаем дрон
print("Close vehicle object")
vehicle.close()

# Завершение работы симулятора
if sitl:
    sitl.stop()
