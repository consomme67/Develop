import datetime
import calendar
import time
import os
import shutil
import subprocess
import RPi.GPIO as GPIO
import requests
import threading

# インターバル
INTERVAL = 0.5
# スリープタイム
SLEEPTIME = 3
# 使用するGPIO
GPIO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

def count_sen():
    # センサー感知
    if (GPIO.input(GPIO_PIN) == GPIO.HIGH):
        nowmil = str(int(time.time() * 1000))
        try:
            with open("/home/pi/doc/central.txt", mode='a') as c:
                c.write(nowmil+'\n')
        except:
            time.sleep(2)
            with open("/home/pi/doc/central.txt", mode='a') as c:
                c.write(nowmil+'\n')
        time.sleep(SLEEPTIME)
    else:
        time.sleep(INTERVAL)

if __name__ == '__main__':
    print("===START===")
    while True:
        count_sen()