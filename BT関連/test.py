
import subprocess

def main():
    command00 = f'ffmpeg -f image2 -r 30 -i pic/%d.jpg -r 15 -an -q:v 0 -y pic/video/video.mp4'
    subprocess.call(command00, shell=True)

"""
        command00 = f'ffmpeg -f image2 -r 12 -i pic/%d.jpg -r 120 -an -vcodec libx264 -pix_fmt yuv420p pic/video/video.mp4'
                f'ffmpeg -seek_timestamp 1 -ss {centime - 5000} -i {input_path} -t 5 -framerate 30\
                    -c:v copy -y /home/pi/doc/mov/cam{cam_num}.mkv'
"""

                #f'ffmpeg -seek_timestamp 1 -ss {centime - 5000} -i {input_path} -t 5 -framerate 30\
                #    -c:v copy -y /home/pi/doc/mov/cam{cam_num}.mkv'


if __name__ == '__main__':
    main()