#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' exam.py программирует дрон для полёта по траектории пятиконечной звезды '''

# Библиотека __future__ нужна для обратной совместимости между python2 и python3
from __future__ import print_function
import math
# Подключаем библиотеку time
import time
# Из библиотеки dronekit подключаем connect для связи с дроном
# VehicleMode для из
# VehicleMode для из

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
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Запускает моторы дрона и поднимает его на высоту равную aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


# Запуск дрона и набор высоты
arm_and_takeoff(10)

print("Set default/target airspeed to 10")
vehicle.airspeed = 10

# Координаты точки взлёта и посадки
lat_h = 55.7514207
long_h = 37.6265806

# Координат широты и долготы каждой точки
latitude_changes = (0.001, 0.002, -0.002, 0.001, -0.002, -0.002, 0.001, -0.002, 0.002, 0.001)
longitude_changes = (-0.002, 0, -0.001, -0.002, 0.001, -0.002, 0.002, 0.001, 0, 0.002)

# Список высот полёта до каждой точки
altitudes = (15, 20, 15, 20, 15, 20)

# Список названий точек
points = ['первой', 'второй', 'третьей', 'четвёртой', 'пятой', 'первой']

# угол поворота дрона начинаем с правого горизонтального луча
angle = math.pi / 2
radius = 0.002

# Дрон облетает месность по траектории звезды
# Через цикл меняем координаты и высоту для каждой точки
for i in range(10):
    if i % 2 == 0:
        print(f"Полёт дрона к points[i] точке полёта в течение 45 секунд на высоте altitudes[i] м.")
        vehicle.simple_goto(LocationGlobalRelative(lat_h + round(radius * 0.38 * math.cos(angle), 6),
                                                   long_h - round(radius * 0.38 * math.sin(angle), 6), 15))
    else:
        print(f"Полёт дрона к points[i] точке полёта в течение 45 секунд на высоте altitudes[i] м.")
        vehicle.simple_goto(LocationGlobalRelative(lat_h + round(radius * math.cos(angle), 6),
                                                   long_h - round(radius * math.sin(angle), 6), 15))
    angle -= math.pi / 5

    # приостанавливаем программу и смотрим движение дрона на карте
    time.sleep(30)

# Отправляем дрон к точке взлёта
print("Квадрокоптер летит к точке взлёта в течение 30 секунд.")
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
