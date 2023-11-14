import telnetlib
import time

HOST = "192.168.2.23"
USER = "admin"
PASS = "tmpgij"

print("==start==")
print()

tn = telnetlib.Telnet(HOST)

#ログイン処理
tn.read_until(b"UserName:")
tn.write(USER.encode('ascii') + b"\n")
if PASS:
    tn.read_until(b"PassWord:")
    tn.write(PASS.encode('ascii') + b"\n")
#<====ここまで

"""ここに送りたいコマンドを記述していく"""
print("flag1")
if tn.read_until(b"#", 2):
    print("flag10")
    exit()
tn.write(b"config ports 1 state enable\n")

print("flag2")
tn.write(b"show ports 1")
#tn.read_until(b'#')
tn.write(b"logout\n")
print("flag3")
#tn.read_until(b'*')
#time.sleep(1)
#print(tn.read_very_eager().decode('ascii'))
#print(tn.read_all().decode('ascii'))
print("flag4")
exit()