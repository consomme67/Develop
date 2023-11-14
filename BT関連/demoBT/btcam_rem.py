import os
from operator import itemgetter
import time

def main():
    filelists = []
    for file in os.listdir("/home/pi/doc/mov"):
        #print(file)
        base, ext = os.path.splitext(file)
        if ext == '.mp4':
            #print("a")
            filelists.append([file, os.path.getctime("/home/pi/doc/mov/"+file)])
    filelists.sort(key=itemgetter(1), reverse=True)
    MAX_CNT = 180

    for i,file in enumerate(filelists):
        if i > MAX_CNT - 1:
            print("/home/pi/doc/mov/"+file[0])
            os.remove("/home/pi/doc/mov/"+file[0])

if __name__ == '__main__':
    while True:
        main()
        print("===")
        time.sleep(60)