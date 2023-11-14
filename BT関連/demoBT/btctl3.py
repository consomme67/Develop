import os
import time
import requests
import glob
import datetime
import math
from pathlib import Path
import re
import subprocess
import numpy as np
import pickle

def main():
    timestamp = check()
    if timestamp:
        for beacon, sensors in timestamp.items():
            for sensor in sensors:

            #各ビーコンとその近似値(センサー)を取得/cut
                for num in range(1, 14, 1):
                    fn = GetFilename(num)
                    if num == 1:
                        check_time(fn, num, sensor)
                    elif num == 2:
                        check_time(fn, num, sensor)
                    else:
                        check_time(fn, num, sensor)
                #結合
                join_frame()
                generateBT()
                send(beacon, "BT")


def check():
    #print("--check--")
    if os.path.isfile("/home/pi/docs/sen/timestamp.txt") and os.path.getsize("/home/pi/docs/sen/timestamp.txt")>0:
        with open("/home/pi/docs/sen/timestamp.txt", mode="r+")as s:
        #with open("/home/pi/docs/sen/GetBeacon.txt", mode="r")as s:
            datadict = pickle.load(s)
            #aaa = s.readlines()
            #print(aaa)
            s.truncate(0)
            """
            for i in aaa:
                with open("/home/pi/timestamp_log.txt", mode="a")as t:
                    t.write(i)
            """
            #print("bbb")
        return datadict


def GetFilename(num):
    q = []
    try:
        k = [os.path.basename(p) for p in glob.glob('/home/pi/docs/mov'+num+'/**', recursive=True) if os.path.isfile(p)]
        for a in k:
            s = a.split('.')[0]
            q.append(s)
        return q
    except:
        return q

def cut_first(timestamp, filename, num):
    tm = timestamp-2
    command02 = f'ffmpeg -ss {tm} -i /home/pi/docs/mov1/{filename}.mp4 -t 2 -movflags faststart \
        -vcodec copy -y /home/pi/BulletTime/first.mp4'
    #command03 = f'ffmpeg -i output.mp4 -framerate 30 -movflags faststart -vcodec libx264 -y /home/pi/hoge.mp4'
    subprocess.call(command02, shell=True)
    #subprocess.call(command03, shell=True)

def cut_last(timestamp, filename, num):
    command02 = f'ffmpeg -ss {timestamp} -i /home/pi/docs/mov2/{filename}.mp4 -t 2 -movflags faststart \
            -vcodec copy -y /home/pi/BulletTime/last.mp4'
    subprocess.call(command02, shell=True)

def cut_tmover(timestamp, filename, num):#終点カメラのタイムスタンプが撮影時間を超えた場合
    command02 = f'ffmpeg -ss {timestamp} -i /home/pi/BulletTime/tmover.mp4 -t 2 -movflags faststart \
        -vcodec copy -y /home/pi/BulletTime/last.mp4'
    #command03 = f'ffmpeg -i /home/pi/tmover.mp4 -framerate 30 -movflags faststart -vcodec libx264 -y /home/pi/hoge.mp4'
    subprocess.call(command02, shell=True)
    #subprocess.call(command03, shell=True)

def cut_tmloss(timestamp, filename, num):#視点カメラのタイムスタンプが撮影時間に足りなかった場合
    tm=timestamp+8
    command02 = f'ffmpeg -ss {tm} -i /home/pi/BulletTime/tmloss.mp4 -t 2 -movflags faststart \
        -vcodec copy -y /home/pi/BulletTime/first.mp4'
    #command03 = f'ffmpeg -i /home/pi/tmloss.mp4 -framerate 30 -movflags faststart -vcodec libx264 -y /home/pi/hoge.mp4'
    subprocess.call(command02, shell=True)
    #subprocess.call(command03, shell=True)

def cut_frame(timestamp, filename, num):
    command04=f'ffmpeg -ss {timestamp} -i "/home/pi/docs/mov{num}/{filename}.mp4 -vframe 1 -vcodec copy -y \
        /home/pi/BulletTime/frame/frame{num-2}.jpeg'
    subprocess.call(command04,shell=True)

def send(timestamp, filename):
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/upload_movie/"
    url2 = 'http://httpbin.org/post'
    HEADERS = {"Content-Type": "multipart/form-data;"}
    tm = timestamp

    video = open('/home/pi/BulleTime/'+filename+'.mp4', 'rb')
    #txt = open('for_send/timestamp.txt', 'rb')

    #    files = {'file_upload': ('hoge.mp4', video, 'video/mp4')}
    #    files = {'file_upload': ('hogehoge.txt', txt, 'text/plain')}
    #    files = {'timestamp': (None, '1611796299', 'text/plain')}

    files = {
        'file_upload': (filename+'.mp4', video, 'video/mp4'),
        'timestamp': (None, tm)
    }

    # data = {'another_key': 'another_value'}
    r = requests.post(url, files=files)

def calc(n,tm2,j):
    print("--calc--")
    print("===========================")
    tm3 = tm2 - j
    print("tm3:")
    print(tm3)
    print(type(tm3))
    time.sleep(5)
    tm4 = tm3.total_seconds()
    print("tm4:")
    print(tm4)
    print(type(tm4))
    tm5 = math.floor(tm4 * 10 ** n) / (10 ** n)
    print("tm5:")
    print(tm5)
    print(type(tm5))
    print("===========================")
    return tm5

def tmover(fn,tm,num):
    fni = [int(s) for s in fn]
    tm2 = datetime.datetime.fromtimestamp(int(tm))
    print("tm2:")
    print(tm2)
    print(type(tm2))
    tm3 = tm2+datetime.timedelta(seconds=10)
    print("tm3:")
    print(tm3)
    print(type(tm3))
    tm4 = int(datetime.datetime.timestamp(tm3))
    print("tm4:")
    print(tm4)
    print(type(tm4))
    idx = np.abs(np.asarray(fni) - tm4).argmin()
    print(fn[idx])
    with open("/home/pi/tmover.ccat", mode="r+") as f:
        f.write("file /home/pi/docs/mov"+num+"/"+tm+".mp4"+"\n")
        f.write("file /home/pi/docs/mov"+num+"/"+fn[idx]+".mp4"+"\n")

    commandc=f'ffmpeg -safe 0 -f concat -i /home/pi/tmover.ccat -vcodec copy -y /home/pi/BulletTime/tmover.mp4'
    subprocess.call(commandc, shell=True)
    return

def tmloss(fn,tm,num):
    fni = [int(s) for s in fn]
    tm2 = datetime.datetime.fromtimestamp(int(tm))
    print("tm2:")
    print(tm2)
    print(type(tm2))
    tm3 = tm2-datetime.timedelta(seconds=10)
    print("tm3:")
    print(tm3)
    print(type(tm3))
    tm4 = int(datetime.datetime.timestamp(tm3))
    print("tm4:")
    print(tm4)
    print(type(tm4))
    idx = np.abs(np.asarray(fni) - tm4).argmin()
    print(fn[idx])
    with open("/home/pi/BulletTime/tmloss.ccat", mode="r+") as f:
        f.write("file /home/pi/docs/mov"+num+"/"+fn[idx]+".mp4"+"\n")
        f.write("file /home/pi/docs/mov"+num+"/"+tm+".mp4"+"\n")

    commandc=f'ffmpeg -safe 0 -f concat -i /home/pi/tmloss.ccat -vcodec copy -y /home/pi/BulletTime/tmloss.mp4'
    subprocess.call(commandc, shell=True)
    return

def join_frame():
    commandm=f'ffmpeg -r 11 -i /home/pi/BulletTime/frame/frame%d.jpeg -vcodec libx264 -pix_fmt yuv420p -r 33 -y \
        /home/pi/BulletTime/frame.mp4'
    subprocess.call(commandm, shell=True)

def generateBT():
    commandg=f'ffmpeg -safe 0 -f concat -i /home/pi/BT.ccat -vcodec copy -y /home/pi/BulletTime/BT.mp4'
    subprocess.call(commandg, shell=True)

def check_time(filenamelist, num, timestamp):
    n = 3
    print("ある")
    for tm in timestamp:
        print(tm)
        tm2 = datetime.datetime.strptime(str(tm.replace("\n", "")), "%Y%m%d%H%M%S.%f")
        for f in filenamelist:
            # print(f)
            j = datetime.datetime.fromtimestamp(float(f))
            if tm2 > j:
                # print("a")
                if tm2 - j < datetime.timedelta(seconds=10):
                    if num==2 and tm2 + datetime.timedelta(seconds=2) > j + datetime.timedelta(seconds=10):
                        print("-=-=-=-=-")
                        tmover(filenamelist, f, num)
                        #time.sleep(10)
                        tm5 = calc(n, tm2, j)
                        cut_tmover(tm5, "hogehoge", num)
                        print("-=-=-=-=-")
                        break
                    elif num==2 and tm2 + datetime.timedelta(seconds=2) < j + datetime.timedelta(seconds=10):
                        print("-=-=-=-=-")
                        tm5 = calc(n, tm2, j)
                        cut_last(tm5, f, num)
                        print("-=-=-=-=-")
                        break
                    elif num==1 and tm2 - datetime.timedelta(seconds=2) < j:
                        print("---===---")
                        tmloss(filenamelist, f, num)
                        tm5 = calc(n, tm2, j)
                        cut_tmloss(tm5, "hogehoge", num)
                        break
                    elif num == 1 and tm2 - datetime.timedelta(seconds=2) > j:
                        print("---===---")
                        tm5 = calc(n, tm2, j)
                        cut_first(tm5, f, num)
                        break
                    elif num!=1 and num!=2:
                        tm5 = calc(n, tm2, j)
                        cut_frame(tm5,f,num)

                elif tm2 - j > datetime.timedelta(minutes=30):
                    print("対象なし")
                    time.sleep(0.1)
                else:
                    time.sleep(0.1)

            else:
                print("f")
                time.sleep(0.1)
    timestamp = []


if __name__=='__main__':
    print("**********start**********")
    while True:
        main()
"""#print(timestamp)
    #print(type(timestamp))
    if timestamp:
        n = 3
        print("ある")
        for tm in timestamp:
            print(tm)
            tm2 = datetime.datetime.strptime(str(tm.replace("\n", "")), "%Y%m%d%H%M%S%f")
            fn = GetFilename()
            print(fn)
            for f in fn:
                #print(f)
                j = datetime.datetime.fromtimestamp(float(f))
                if tm2>j:
                    #print("a")
                    if tm2-j < datetime.timedelta(seconds=10):
                        if tm2+datetime.timedelta(seconds=2) > j+datetime.timedelta(seconds=10):
                            print("-=-=-=-=-")
                            tmover(fn, f)
                            tm5 = calc(n, tm2, j)
                            cut_tmover(tm5, "hogehoge")
                            send(tm, "hoge")
                            print("send:" + tm)
                            print("-=-=-=-=-")
                            break
                        elif tm2-datetime.timedelta(seconds=2) < j:
                            print("---===---")
                            tmloss(fn, f)
                            tm5 = calc(n, tm2, j)
                            cut_tmloss(tm5, "hogehoge")
                            send(tm, "hoge")
                            print("send:" + tm)
                            print("---===---")
                            break
                        else:
                            tm5 = calc(n, tm2, j)
                            cut(tm5, f)
                            send(tm, "hoge")
                            print("send:" + tm)
                            break
                    elif tm2-j > datetime.timedelta(minutes=30):
                        print("c")
                        time.sleep(0.1)
                    else:
                        time.sleep(0.1)

                else:
                    print("f")
                    time.sleep(0.1)
        timestamp = []
    else:
        #print("ない")
        time.sleep(1)
        return"""