import subprocess as sb

cm = f'ffmpeg -f image2 -r 12 -i pic/%d.jpg -r 60 -vcodec libx264 -pix_fmt yuv420p -y pic/video/video.mp4'

sb.call(cm, shell=True)

