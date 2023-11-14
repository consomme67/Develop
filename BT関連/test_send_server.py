import requests

def send():
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/upload_movie/"
    url2 = 'http://httpbin.org/post'
    HEADERS = {"Content-Type": "multipart/form-data;"}

    video = open('for_send/WIN_20210212_13_18_37_Pro.mp4', 'rb')
    txt = open('for_send/timestamp.txt', 'rb')

#    files = {'file_upload': ('hoge.mp4', video, 'video/mp4')}
#    files = {'file_upload': ('hogehoge.txt', txt, 'text/plain')}
#    files = {'timestamp': (None, '1611796299', 'text/plain')}

    files = {
        'file_upload': ('hoge.mp4', video, 'video/mp4'),
        'timestamp': (None, '1611796299')
    }

    #data = {'another_key': 'another_value'}
    r = requests.post(url, files=files)
    print(r.url)
    print(r.text)
    print(r.status_code)
    print(r.content)

def get():
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/get_beacon_timestamp_list/"
    #?timestamp=1614923129
    files = {
        'timestamp': '1614923129'
    }
    r = requests.get(url, params=files)
    ttt = r.text
    print(type(r.json()))
    #print(r.url)
    #print(r.text)
    #print(r.status_code)
    #print(r.content)
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/get_beacon_timestamp_list/"
    #?timestamp=1614923129
    files = {
        'timestamp': '1614923130'
    }
    r = requests.get(url, params=files)
    print(r.url)
    print(r.text)
    print(r.status_code)
    print(r.content)

def beacon_GET(lasttime):
    """鯖からとってきてキュー作ってそこにＩＤとtimestamp放り込む"""
    tm = lasttime
    aaa = None
    url = "https://sirius.e-catv.ne.jp/shimanami_movie/int/api/get_beacon_timestamp_list/"
    files = {
        'timestamp': tm
    }
    r = requests.get(url, params=files)
    return r.json(),aaa

def test():
    bb = beacon_GET(0)
    try:
        bb[1]
        print(bb[0])
    except:
        print("無し")
        return
    print("koko")
if __name__ == "__main__":
    test()
    #test