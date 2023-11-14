from datetime import datetime
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

def beacon_GET(lasttime):
    """鯖からとってきてキュー作ってそこにＩＤとtimestamp放り込む"""
    tm = lasttime
    aaa = ''
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/get_beacon_timestamp_list/"
    files = {
        'timestamp': tm
    }
    r = requests.get(url, params=files)

    return r.json()
def near_out():
    """absでキュー内のtimestampと↓のcentralの中との近似値とる"""
    return



def count_sen():
    while True:
        # センサー感知
        if (GPIO.input(GPIO_PIN) == GPIO.HIGH):
            nowmil = str(int(time.time() * 1000))
            try:
                with open("/home/pi/doc/central.txt", mode='a') as c:
                    c.write(nowmil+'\n')
            except:
                time.sleep(1)
                with open("/home/pi/doc/central.txt", mode='a') as c:
                    c.write(nowmil+'\n')
            time.sleep(SLEEPTIME)
        else:
            time.sleep(INTERVAL)

def main(starttime):
    sen = threading.Thread(target=count_sen)
    catch = threading.Thread(target=beacon_GET, args=starttime)
    sen.setDaemon(True)
    catch.setDaemon(True)
    sen.start()
    catch.start()


if __name__ == '__main__':
    print("===START===")
    beacon_GET(0)