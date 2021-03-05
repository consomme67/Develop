import queue
import requests
import os
import subprocess

def kinnjiti_central():
    #fxt = os.stat("ファイルパス").st_size == 0
    fxt = os.stat("textTest").st_size == 0
    print(fxt)

    if not fxt:
        aaa = []
        nearTime = queue.Queue()
        with open("textTest") as t:
            nt = t.readlines()
        for i in nt:
            nearTime.put(i.split())

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

def cut():
    print("cut処理")
    print("各カメラフォルダからnearTimeキューから出したタイムで切り出し")
    print("それぞれのファイルを共有フォルダからコピーする？")
    print("切り出し方は1,2はカット，3-...はフレームで")
    #始点カメラ用(-5秒から5秒間)
    command01 = f'ffmpeg -seek_timestamp 1 -ss {centime - 5000} -i {input_path} -t 5 -framerate 30\
            -c:v copy -y /home/pi/doc/mov/cam{cam_num}.mkv'
    subprocess.call(command01, shell=True)
    #終点カメラ用(+1秒から5秒間)
    command02 = f'ffmpeg -seek_timestamp 1 -ss {centime + 1000} -i {input_path} -t 5 -framerate 30\
            -c:v copy -y /home/pi/doc/mov/cam{cam_num}.mkv'
    subprocess.call(command02, shell=True)
    #中間フレーム用
    #11枚の画像を33ミリ秒毎に切り出す(for文で(i++))
    i=1
    while i<12:
        j=i*33 #11枚(1枚3フレずつ=990ミリ秒≒1秒と考える)
        command03 = f'ffmeg -seek_timestamp 1 -ss {centime + j} -i {各フォルダ} -r 30 \
                -vframes 1 {output_path}~~~~{i}.png'
        i=+1
def test():
    a=0
    while a<11:
        b = a*3*33
        print(a,b)
        a+=1
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
    main_que = kinnjiti_central()

    print("==main==")
    if not main_que.empty():
        i = int(main_que.get()[0])
        print(i)
    else:
        print("queの中身無いから戻す")
        return


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
    test()
