import subprocess

def MainCap(dev_num, cam_num):

    command04 = f'ffmpeg -f v4l2 -input_format mjpeg -video_size 1920x1080 -framerate 30 \
            -ts mono2abs -i /dev/video0 -c:v copy \
            -f segment -strftime 1 -segment_time 5 -segment_format mkv -segment_wrap 6 \
            /home/pi/docs/mov/%Y-%m-%d-%H-%M-%S.mkv'

    subprocess.call(command04, shell=True)