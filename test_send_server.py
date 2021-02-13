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
    print(r.text)
    print(r.status_code)
    print(r.content)

if __name__ == "__main__":
    send()
    #test