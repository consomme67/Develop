from datetime import datetime
import calendar
import time
import os
import shutil
import subprocess
import RPi.GPIO as GPIO

# インターバル
INTERVAL = 0.5
# スリープタイム
SLEEPTIME = 3
# 使用するGPIO
GPIO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

def kokoha_GET():
	"""鯖からとってきてキュー作ってそこにＩＤとtimestamp放り込む"""
	return
def kinjiti_out():
	"""absでキュー内のtimestampと↓のcentralの中との近似値とる"""
	return



def count_sen():
	while True:
		# センサー感知
		if (GPIO.input(GPIO_PIN) == GPIO.HIGH):
			nowmil = str(int(time.time() * 1000))
			with open("/home/pi/doc/central.txt", mode='a') as c:
				c.write(nowmil+'\n')
			time.sleep(SLEEPTIME)
		else:
			time.sleep(INTERVAL)

GPIO.cleanup()


if __name__ == '__main__':
	print("===START===")


	time.sleep(3)
	count_sen()