import requests
import time
import datetime
import os
import pickle

def main(firsttime):
    pass

def beacon_GET(lasttime):
    """鯖からとってきてキュー作ってそこにＩＤとtimestamp放り込む"""
    tm = int(lasttime)
    aaa = None
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/get_beacon_timestamp_list/"
    files = {
        'timestamp': tm
    }
    r = requests.get(url, params=files)
    #with open("/home/pi/doc/sen/GetBeacon.txt", mode="a")as s:
    #    s.readlines()
    return r.json(),aaa

def check(beaconlist):
    if os.path.isfile("/home/pi/doc/sen/sensor.txt") and os.path.getsize("/home/pi/doc/sen/sensor.txt")>0:
        with open("/home/pi/doc/sen/sensor.txt", mode="r+")as s:
        #with open("/home/pi/docs/sen/GetBeacon.txt", mode="r")as s:
            aa = s.readlines()
            print(aa)
            aaa = []
            for item in aa:
                aaa.append(int(item.replace("\n", ""))/1000)
                print("===")
                print(aaa)
            #print(aaa)
        sendic = {}

        if aaa:
            print("a")
            for item in beaconlist:
                print("b")
                li = []
                i = datetime.datetime.strptime(item, "%Y%m%d%H%M%S%f")
                print("c")
                for jj in aaa:
                    print("d")
                    print(type(jj))
                    print(jj)
                    j = datetime.datetime.strptime(str(jj), "%Y%m%d%H%M%S.%f")
                    print("e")
                    if i<j and j-i < datetime.timedelta(seconds=20):
                        print("f")
                        print(j-i)
                        li.append(jj)
                        #sendic.setdefault(item, []).append(jj)
                        #sendic[item].append(jj)
                print(li)
                if li:
                    sendic[item]=li

            #print(aaa)
                #print("bbb")
            print("----")
            print(sendic)
            print("----")
            return sendic
        else:
            return 2
    else:
        #エラー(ビーコン取得するがセンサーに反応なし)
        #print("aaaaaaa")
        return 1

def dump(be_se_dict):
    with open("/home/pi/doc/sen/timestamp.txt", mode="wb") as file:
        pickle.dump(be_se_dict, file)
    time.sleep(1)

if __name__ == '__main__':
    print("********START********")
    lasttime = 20210101000000000
    while True:
        try:
            i = beacon_GET(lasttime)[0]
            if not len(i) == 0:
                print(i)
                with open("/home/pi/doc/sen/GetBeacon.txt", mode="a") as f:
                    for j in i:
                        f.write(str(j) + "\n")
                lasttime = j
                #time.sleep(20)
                print("b")
                b_s_dict = check(i)
                print(b_s_dict)
                if b_s_dict==1 or b_s_dict==2:
                    print("error")
                    continue
                print("kkkkk")
                dump(b_s_dict)
                time.sleep(30)
            else:
                time.sleep(30)
        except:
            print("notAccess...")
            time.sleep(30)