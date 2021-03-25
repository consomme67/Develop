import requests
import time

def main(firsttime):


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



if __name__ == '__main__':
    print("********START********")
    lasttime = 0
    while True:
        try:
            i = beacon_GET(lasttime)[0]
            if not len(i) == 0:
                print(i)
                with open("/home/pi/doc/sen/timestamp.txt", mode="a") as f:
                    for j in i:
                        f.write(str(j) + "\n")
                lasttime = j
                time.sleep(30)
            else:
                time.sleep(30)
        except:
            print("notAccess...")
            time.sleep(30)