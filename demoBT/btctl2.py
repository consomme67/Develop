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

def main():
    timestamp = check()
    #print(timestamp)
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
        return


def check():
    #print("--check--")
    if os.path.isfile("/home/pi/docs/sen/timestamp.txt") and os.path.getsize("/home/pi/docs/sen/timestamp.txt")>0:
        with open("/home/pi/docs/sen/timestamp.txt", mode="r+")as s:
        #with open("/home/pi/docs/sen/GetBeacon.txt", mode="r")as s:
            aaa = s.readlines()
            #print(aaa)
            s.truncate(0)
            for i in aaa:
                with open("/home/pi/timestamp_log.txt", mode="a")as t:
                    t.write(i)
            #print("bbb")
        return aaa
    else:
        #print("aaaaaaa")
        return

def GetFilename():
    q = []
    try:
        k = [os.path.basename(p) for p in glob.glob('/home/pi/docs/mov2/**', recursive=True) if os.path.isfile(p)]
        for a in k:
            s = a.split('.')[0]
            q.append(s)
        return q
    except:
        return q

def cut(timestamp, filename):
    command02 = f'ffmpeg -ss {timestamp} -i /home/pi/docs/mov2/{filename}.mp4 -t 2 -movflags faststart \
        -vcodec copy -y /home/pi/output.mp4'
    command03 = f'ffmpeg -i output.mp4 -framerate 30 -movflags faststart -vcodec libx264 -y /home/pi/hoge.mp4'
    subprocess.call(command02, shell=True)
    subprocess.call(command03, shell=True)

def cut_tmover(timestamp, filename):
    command02 = f'ffmpeg -ss {timestamp} -i /home/pi/BulletTime/tmover.mp4 -t 2 -movflags faststart \
        -vcodec copy -y /home/pi/tmover.mp4'
    command03 = f'ffmpeg -i /home/pi/tmover.mp4 -framerate 30 -movflags faststart -vcodec libx264 -y /home/pi/hoge.mp4'
    subprocess.call(command02, shell=True)
    subprocess.call(command03, shell=True)

def cut_tmloss(timestamp, filename):
    tm=timestamp+8
    command02 = f'ffmpeg -ss {tm} -i /home/pi/BulletTime/tmloss.mp4 -t 2 -movflags faststart \
        -vcodec copy -y /home/pi/tmloss.mp4'
    command03 = f'ffmpeg -i /home/pi/tmloss.mp4 -framerate 30 -movflags faststart -vcodec libx264 -y /home/pi/hoge.mp4'
    subprocess.call(command02, shell=True)
    subprocess.call(command03, shell=True)

def send(timestamp, filename):
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/upload_movie/"
    url2 = 'http://httpbin.org/post'
    HEADERS = {"Content-Type": "multipart/form-data;"}
    tm = timestamp

    video = open('/home/pi/'+filename+'.mp4', 'rb')
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

def tmover(fn,tm):
    fni = [int(s) for s in fn]
    tm2 = datetime.datetime.fromtimestamp(int(tm))
    print("tm2:")
    print(tm2)
    print(type(tm2))
    tm3 = tm2+datetime.timedelta(seconds=60)
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
        f.write("file /home/pi/docs/mov2/"+tm+".mp4"+"\n")
        f.write("file /home/pi/docs/mov2/"+fn[idx]+".mp4"+"\n")

    commandc=f'ffmpeg -safe 0 -f concat -i /home/pi/tmover.ccat -vcodec copy -y /home/pi/BulletTime/tmover.mp4'
    subprocess.call(commandc, shell=True)
    return

def tmloss(fn,tm):
    fni = [int(s) for s in fn]
    tm2 = datetime.datetime.fromtimestamp(int(tm))
    print("tm2:")
    print(tm2)
    print(type(tm2))
    tm3 = tm2-datetime.timedelta(seconds=60)
    print("tm3:")
    print(tm3)
    print(type(tm3))
    tm4 = int(datetime.datetime.timestamp(tm3))
    print("tm4:")
    print(tm4)
    print(type(tm4))
    idx = np.abs(np.asarray(fni) - tm4).argmin()
    print(fn[idx])
    with open("/home/pi/tmloss.ccat", mode="r+") as f:
        f.write("file /home/pi/docs/mov2/"+fn[idx]+".mp4"+"\n")
        f.write("file /home/pi/docs/mov2/"+tm+".mp4"+"\n")

    commandc=f'ffmpeg -safe 0 -f concat -i /home/pi/tmloss.ccat -vcodec copy -y /home/pi/BulletTime/tmloss.mp4'
    subprocess.call(commandc, shell=True)
    return
if __name__=='__main__':
    print("**********start**********")
    while True:
        main()
