
import subprocess

def main():
    command00 = f'ffmpeg -f image2 -r 15 -i pic/%d.jpg -r 45 -vcodec libx264 -pix_fmt yuv420p pic/video/video.mp4'


                #f'ffmpeg -seek_timestamp 1 -ss {centime - 5000} -i {input_path} -t 5 -framerate 30\
                #    -c:v copy -y /home/pi/doc/mov/cam{cam_num}.mkv'

    subprocess.call(command00, shell=True)

if __name__ == '__main__':
    main()