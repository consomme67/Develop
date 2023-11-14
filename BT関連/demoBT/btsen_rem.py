import time

if __name__ == '__main__':
    while True:
        senlist = []
        #sen_timestamp見に行って，リスト化.要素数が50個超える場合30になるまで削除
        with open("", mode="r+")as f:
            senlist.append(f.readlines())

        time.sleep(600)