import os
import shutil
import subprocess
import time as tm
import threading


def main_cap(dev_num, cam_num):
    input_path = "/dev/video" + dev_num
    output_path = "/home/pi/mov/cam" + cam_num
    print(output_path)
    command01 = f'ffmpeg -f v4l2 -input_format mjpeg -t 00:00:10 -framerate 30 -video_size 1920x1080 \
        -ts mono2abs -i {input_path}  -r 2997/100 -f matroska -c:v copy -g 1 -y\
        -copyts {output_path}.mkv'
    subprocess.call(command01, shell=True)

def send_file(ob1, to1, to2):
    command_send = f'sshpass -p "pi" scp -r /home/pi/{ob1} pi@{to1}.local:/home/pi/{to2}'
    subprocess.call(command_send, shell=True)
    print("==send==")

def judge():
    with open("/home/pi/doc/stop.txt", mode='x') as stop:
        pass
    send_file("doc/stop.txt", "ras-ctl", "doc")
    cen = []
    while True:
        ceexist = os.path.exists("/home/pi/doc/central.txt")
        noexist = os.path.exists("/home/pi/doc/nobody.txt")
        if ceexist:
            flag = True
            with open('central.txt', mode='r') as f:
                centime = f.readlines()
            for i in centime:
                cen.append(int(int(i.strip())/1000))
            return flag, cen

        elif noexist:
            flag = False
            with open('/home/pi/doc/start.txt', mode='r') as start:
                pass
            #com1 = 'zip /home/pi/doc/mov.zip /home/pi/doc/mov'
            com2 = 'scp /home/pi/doc/start.txt tsuna@desktop-coscjj3.local'
            #subprocess.call(com1, shell=True)
            subprocess.call(com2, shell=True)
            #send_file("doc/start.txt", "ras-ctl", "doc")
            return flag

def frame(cam_num, centime):

    input_path = "/home/pi/doc/mov/cam" + cam_num + ".mkv"
    command02 = f'ffmpeg -seek_timestamp 1 -ss {centime} -i {input_path} -t 1 -vframes:v 30 \
     -framerate 30 -c:v copy -y /home/pi/doc/frame/cam{cam_num}.jpg'
    subprocess.call(command02, shell=True)

def main():
    cam1 = threading.Thread(target=main_cap, args=("0", "3"))
    cam2 = threading.Thread(target=main_cap, args=("2", "4"))

    cam1.setDaemon(True)
    cam2.setDaemon(True)

    cam1.start()
    cam2.start()

    cam1.join()
    cam2.join()

    result = judge()
    if result[0]:
        for i in result[1]:
            cam1 = threading.Thread(target=frame, args=("3", i))
            cam2 = threading.Thread(target=frame, args=("4", i))
            cam1.setDaemon(True)
            cam2.setDaemon(True)
            cam1.start()
            cam2.start()
            cam1.join()
            cam2.join()

        send_file("doc/mov", "ras-ctl", "doc")
        shutil.rmtree("/home/pi/doc/*")
    else:
        shutil.rmtree("/home/pi/doc/*")

if __name__ == '__main__':
# カメラ1&2の保存用ファイル作成
    fexist = os.path.exists("/home/pi/doc/mov")
    if fexist:
        shutil.rmtree("/home/pi/doc/mov")
        os.mkdir("/home/pi/doc/mov")
    else:
        os.mkdir("/home/pi/doc/mov")

    while True:
        stexist = os.path.exists("/home/pi/doc/start_cam.txt")  # スタート用ファイル確認
        if stexist:
            with open("/home/pi/doc/start_sen.txt", mode='x') as sensor:
                pass
            send_file("doc/start_sen.txt", "ras-ctl", "doc")
            main()
        """
        enter = input(">>>")
        if enter == "":
            main()
        elif enter == "n" or "q" or "no" or "quit":
            print("Bye")
            exit()
        else:
            print("What?")
        """