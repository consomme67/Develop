import os
import subprocess

def MainCap(dev_num, cam_num):
    input_path = "/dev/video" + dev_num
    output_path = "/home/pi/docs/mov/"
    print(output_path)
    command01 = f'ffmpeg -f v4l2 -input_format mjpeg -t 00:10:00 -framerate 30 -video_size 1920x1080 \
        -ts mono2abs -i {input_path}  -r 2997/100 -f matroska -c:v copy -g 1 -y\
        -copyts {output_path}.mkv'

    command02 = f'ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -f segment -video_size 1920x1080 \
        -ts mono2abs -i {input_path}   -c:v copy -y\
        -copyts -segment_time 00:10:00 {output_path}%02d.mkv'
    subprocess.call(command02, shell=True)

if __name__ == "__main__":
#    ste == os.path.exists("/home/pi/doc/start.txt")

    MainCap("0", "1")
