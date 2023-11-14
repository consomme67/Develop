import queue
import requests
import os
import subprocess
import time

def kinnjiti_central():
    #fxt = os.stat("ファイルパス").st_size == 0
    fxt = os.stat("textTest").st_size == 0
    #print(fxt)

    if not fxt:
        aaa = []
        nearTime = queue.Queue()
        with open("textTest", mode="r+") as t:
            nt = t.readlines()
            t.truncate(0)
        for i in nt:
            nearTime.put(i.split())
            if not os.path.exists("time_log"):
                with open("time_log", mode="w") as l:
                    l.write("")
            with open("time_log", mode="a") as l:
                l.write(i+"\n")


        #print(nearTime.empty())
        #print(type(nearTime.get()))
        #k = int(nearTime.get()[0])

        #print(nearTime.get())
        #print(nearTime.empty())
        return nearTime
    else:
        return

"""
    if not fxt:
        nt = []
        nearTime = queue.Queue()
        with open("読み込むテキスト絶対パス", mode="a") as t:
            nt = t.readlines()
            t.write("ここでファイルクリア")
        for i in nt:
            nearTime.put(i.strip())

    else:
        return
"""

def cut(time):
    print("cut処理")
    print("各カメラフォルダからnearTimeキューから出したタイムで切り出し")
    #それぞれのファイルを共有フォルダからコピーする？
    #切り出し方は1,2はカット，3-...はフレームで
    #始点カメラ用(-5秒から5秒間)
    command01 = f'ffmpeg -seek_timestamp 1 -ss {centime - 5000} -i {input_path} -t 5 \
            -framerate 30 -c:v copy -y /home/pi/doc/mov/cam{cam_num}.mkv'
    subprocess.call(command01, shell=True)
    #終点カメラ用(0秒から5秒間)
    command02 = f'ffmpeg -seek_timestamp 1 -ss {centime} -i {input_path} -t 5 -framerate 30 \
            -c:v copy -y /home/pi/doc/mov/cam{cam_num}.mkv'
    subprocess.call(command02, shell=True)
    #中間フレーム用
    #11枚の画像を33ミリ秒毎に切り出す(for文で(i++))
    i=1
    while i<12:
        j=i*33 #11枚(1枚3フレずつ=990ミリ秒≒1秒と考える)
        command03 = f'ffmeg -seek_timestamp 1 -ss {centime + j} -i {各フォルダ} -r 30 \
                -vframes 1 {output_path}~~~~{i}.png'
        subprocess.call(command03, shell=True)
        i=+1

def generate(time):
    #切り出したフレームを結合
    command00 = f'ffmpeg -f image2 -r 30 -i pic/%d.jpg -r 15 -an -q:v 0 -y pic/video/video.mp4'
    subprocess.call(command00, shell=True)
    #始+中+終を結合
    command01 = f'ffmpeg -f concat -i {ファイル名} -c copy output.mp4'


def send():
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/upload_movie/"
    video = open('for_send/WIN_20210212_13_18_37_Pro.mp4', 'rb')
    files = {
        'file_upload': ('hoge.mp4', video, 'video/mp4'),
        'timestamp': (None, '1611796299')
    }
    r = requests.post(url, files=files)
    return

def main():
    print("==main==")
    main_que = kinnjiti_central()
    while True:
        try:
            i = int(main_que.get()[0])
            print(i)
            cut(i)
            generate(i)
            send()
        except:
            print("--nothing--")
            return

"""
    if not main_que.empty():
        i = int(main_que.get()[0])
        print(i)
    elif not main_que.empty():
        print("queの中身無いから戻す")
    return
"""

"""
def hoge():
    a=1
    b=2
    c="ccc"

    que = queue.Queue()

    que.put(a)
    print(que)
    que.put(c)

    while not que.empty():
        print(que.get())
"""




if __name__=='__main__':
    print("==start==")
    while True:
        main()
        time.sleep(2)
