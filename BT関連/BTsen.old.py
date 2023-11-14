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

def count_sen():
	os.mkdir("/home/pi/doc/frame")
	os.mkdir("/home/pi/doc/seg")
	while True:
		# センサー感知
		if (GPIO.input(GPIO_PIN) == GPIO.HIGH):
			#now = datetime.utcnow()
			#print(calendar.timegm(now.utctimetuple()))
			nowmil = str(int(time.time() * 1000))
			with open("/home/pi/doc/central.txt", mode='a') as c:
				c.write(nowmil+'\n')
			time.sleep(SLEEPTIME)
		else:
			stexist = os.path.exists("/home/pi/doc/stop.txt")
			if stexist:
				ceexist = os.path.exists("/home/pi/doc/central.txt")
				if ceexist:
					send_to_cam("central")
				else:
					with open("/home/pi/doc/nobody.txt", mode='x') as n:
						pass
					send_to_cam("nobody")
				time.sleep(1)
				break

			#5分間撮影後の合図用ファイル確認&送信
			time.sleep(INTERVAL)

	while True: #あればまとめて送信，なければ次へ
		nobexist = os.path.exists("/home/pi/doc/nobody_cam.txt")
		movexist = os.path.exists("/home/pi/doc/mov")
		if nobexist:
			#開始用，中心点，合図用それぞれのファイルを削除
			shutil.rmtree("/home/pi/doc/*")
			GPIO.cleanup()
			break
		elif movexist:
			if len([iq for iq in os.scandir("/home/pi/doc/frame")]) <= 2: #フレーム用のカメラの台数
				shutil.move("/home/pi/doc/mov", "/home/pi/doc/seg")
				shutil.move("/home/pi/doc/frame", "/home/pi/doc/seg")
				#動画生成機へ投げる
				com = 'sshpass -p "pi" scp -r /home/pi/doc/seg /home/pi/'
				shutil.rmtree("/home/pi/doc/*")
				GPIO.cleanup()
				break


def send_to_cam(cm):
	filecm = cm
	for num in range(1, 2):
		command_send = f'sshpass -p "pi" scp /home/pi/doc/{filecm}.txt ras-cam{num}.local:/home/pi/doc'
		subprocess.call(command_send, shell=True)

if __name__ == '__main__':
	print("===START===")
	docexist = os.path.exists("/home/pi/doc/")
	if not docexist:
		os.mkdir("/home/pi/doc/")
	with open("/home/pi/doc/start_cam.txt", mode='x') as n:
		pass
	send_to_cam("start_cam")
	time.sleep(3)
	count_sen()
	#while True:
		#fexist = os.path.exists("/home/pi/doc/start_sen.txt")  # スタート用ファイル確認
		#if fexist:
		#	count()