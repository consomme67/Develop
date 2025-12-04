import queue
import threading
import time
#from symbol import return_stmt

import cv2
from scapy.all import *
import socket
import sys
import netifaces
import argparse
from datetime import datetime
import struct
import urllib.parse
import xml.etree.ElementTree as ET
from io import BytesIO
import schedule
import requests
import json
import paho.mqtt.client as mqtt
import random

from scapy.layers.inet import TCP, UDP

# パケット処理用キュー
packet_queue = queue.Queue()
# キャプチャ停止フラグ (グローバル変数)
stop_capture = False
# RTP-107パケット専用キュー
queue_size = 10
rtp_107_queue = queue.Queue(maxsize=queue_size)
exec_queue = queue.LifoQueue(maxsize=queue_size)
rtp_107_packets = []
namespaces = {'tt': 'http://www.onvif.org/ver10/schema'}
payload_data = ""
xml_buffer = b''
wait_time = 10
pic_quality = 80
mac_address = ""
mqtt_client_obj = None
capture_queue = deque(maxlen=1)
frame_buffer = threading.Lock()

config = open('./config.json', 'r')
data = json.load(config)

name = data['name']
user = data['user']
password = urllib.parse.quote_plus(data['password'])
server_ip = data['cam_ip']
url = data['rtsp_url']

broker_ip = data['mqtt_connect']['broker_ip']
mqtt_port = data['mqtt_connect']['port']
mqtt_user = data['mqtt_connect']['user']
mqtt_password = data['mqtt_connect']['password']
topic = data['mqtt_connect']['topic']
client_id = f'mqtt-client-{random.randint(0, 1000)}'


def is_rtp_packet(data):
    """データがRTPパケットかどうかを判定する"""
    # RTPパケットの最小サイズは12バイト
    if len(data) < 12:
        return False

    # RTPの最初の2ビットは通常バージョンを示す（2の場合は0x80, 0x90等）
    first_byte = data[0]

    # 一般的なRTPバージョン2のパケットかチェック
    if (first_byte & 0xC0) == 0x80:  # 0x80 = 10000000
        return True

    return False


def is_rtsp_interleaved(data):
    """RTSP Interleavedフレームかどうかを判定する"""
    # RTSPインターリーブドフレームは$ (0x24)で始まる
    while data and data[0] != 0x24:
        data = data[1:]

    if len(data) < 4:  # $ + channel + length (2 bytes)
        return False

    if data[0] == 0x24:  # $
        return True

    return False


def extract_rtp_from_interleaved(data):
    #print(f"確認：{data}")
    """RTSPインターリーブドフレームからRTPデータを抽出する"""
    # $, チャネル番号, 長さ(2バイト)の後にRTPデータがある
    if len(data) < 4:
        return None

    # データ長を取得 (ビッグエンディアン)
    length = (data[2] << 8) | data[3]

    # データ長チェック
    if len(data) < length + 4:
        return None

    # RTPデータ部分を抽出
    rtp_data = data[4:4 + length]

    return rtp_data


def get_rtp_payload_type(data):
    """RTPパケットからペイロードタイプを抽出する"""
    if not is_rtp_packet(data):
        return None

    # RTPヘッダーの2バイト目の下位7ビットがペイロードタイプ
    pt = data[1] & 0x7F
    return pt


def rtsp_rtp_filter(packet):
    global xml_buffer
    """RTSPパケットまたはRTPパケットかどうかを判定するフィルタ関数"""
    # RTSPパケット（TCP/554）をチェック
    if TCP in packet:
        if packet[TCP].sport == 554:
            # TCPペイロードがある場合
            if Raw in packet:
                payload = packet[Raw].load

                # RTSPコマンドチェック
                try:
                    payload_str = payload.decode('utf-8', errors='ignore')
                    # RTSPメソッド（DESCRIBE, SETUP, PLAY, TEARDOWN等）を検出
                    if re.search(r'(DESCRIBE|SETUP|PLAY|PAUSE|TEARDOWN|OPTIONS|GET_PARAMETER)\s', payload_str):
                        return True
                except:
                    pass

                # RTSPインターリーブドフレーム（RTP over TCP）をチェック
                if is_rtsp_interleaved(payload):
                    rtp_data = extract_rtp_from_interleaved(payload)
                    if rtp_data and is_rtp_packet(rtp_data):
                        pt = get_rtp_payload_type(rtp_data)
                        if pt == 107:
                            rtp_payload = rtp_data[12:]

                            xml_buffer += rtp_payload
                            if xml_buffer.endswith(b'</tt:MetadataStream>'):
                                end_idx = xml_buffer.find(b'</tt:MetadataStream>') + len(b'</tt:MetadataStream>')
                                complete_xml = xml_buffer[:end_idx]
                                rtp_107_queue.put(complete_xml)

                                #print(len(exec_queue.queue))
                                if queue_size/2 <= len(exec_queue.queue):
                                    #print("size over")
                                    exec_queue.queue.pop()
                                #print("put")
                                exec_queue.put(complete_xml)
                                xml_buffer = xml_buffer[end_idx:]
                                #print(rtp_107_queue)
                                #xml_buffer = b''
                            # RTP-107パケットを特別に記録 (パケット全体とRTPデータを含む)
                            #rtp_107_queue.put((packet, rtp_data))
                            return True
                    return True

            return True

def packet_callback(packet):
    """パケットを受信したときに呼び出されるコールバック関数"""
    global payload_data

    if rtsp_rtp_filter(packet):
        # キューにパケットを追加
        packet_queue.put(packet)

        # RTSPパケットの解析
        if TCP in packet and Raw in packet:
            payload = packet[Raw].load
            # RTSPコマンドの検出
            try:
                payload_str = payload.decode('utf-8', errors='ignore')
                rtsp_match = re.search(r'(DESCRIBE|SETUP|PLAY|PAUSE|TEARDOWN|OPTIONS|GET_PARAMETER)\s', payload_str)
                if rtsp_match:
                    rtsp_cmd = rtsp_match.group(1)
                    print(f"\n[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] RTSP コマンド: {rtsp_cmd}")
                    print(f"  {packet.summary()}")
                    print(f"  ペイロード先頭: {payload_str[:100]}")
            except:
                pass

            # インターリーブドRTPの検出
            if is_rtsp_interleaved(payload):
                rtp_data = extract_rtp_from_interleaved(payload)
                if rtp_data and is_rtp_packet(rtp_data):
                    pt = get_rtp_payload_type(rtp_data)
                    if pt == 107:
                        csrc_count = rtp_data[0] & 0x0F
                        if len(rtp_data) > 12:
                            header_size = 12 + (4 * csrc_count)
                            if header_size < len(rtp_data):
                                payload_data = rtp_data[header_size:]


def xml_107_analyze():
    global exec_queue
    a = ""
    payload_data = exec_queue.get()
    try:

        tree = ET.parse(BytesIO(payload_data))
        root = tree.getroot()

    except:
        print("==except==")
        print(payload_data)
        print("====")
        return

    print("====")
    frame = root.find('.//tt:Frame', namespaces)
    utc_time = frame.get('UtcTime') if frame is not None else "時刻情報なし"
    print(utc_time)
    a += "{"
    a += '"timestamp" : "' + utc_time + '",'
    a += '"Objects" : {'

    object_count_elem = root.find('.//Property[@name="ObjectCount"]')
    object_count = object_count_elem.text if object_count_elem is not None else "不明"
    print(object_count)

    objects = root.findall('.//tt:Object', namespaces)

    for i, obj in enumerate(objects):
        print(f"\n--- オブジェクト {i + 1} ---")

        # オブジェクトID
        obj_id = obj.get('ObjectId')
        print(f"ID: {obj_id}")

        speed_elem = obj.find('.//tt:Speed', namespaces)
        if speed_elem is not None:
            speed = speed_elem.text
            print(f"速度: {speed}")
        mes = '"' + str(obj_id) + '" : "' + str(speed) + '",'
        a += mes
    print("===")

    frame_data = get_frame()
    a = a[0:-1]
    a += '},'
    a += '"MACaddress" : "' + mac_address + '",'
    a += '"name" : "' + name + '",'
    a += '"frame_data" : "' + frame_data + '"}'
    json_send = json.dumps(a)
    #json_send = a
    #print(json_send)
    #print(mac_address)
    #print(name)
    #print(json_send)
    mqtt_client_obj.publish(topic, json_send)

    return

def get_frame():
    global capture_queue
    with frame_buffer:
        if frame_buffer:
            latest_frame = capture_queue[-1].copy()
        else:
            latest_frame = None
    if latest_frame is not None:
        ret, jpeg = cv2.imencode('.jpg', latest_frame, [int(cv2.IMWRITE_JPEG_QUALITY), pic_quality])
        if ret:
            data = jpeg.tobytes()
            b64_str = base64.b64encode(jpeg).decode('ascii')
    else:
        data = None
    return b64_str


    latest_frame = capture_queue.get()

    if capture_queue.full():
        print("full")

    return latest_frame

def scheduler_exec():
    """スケジューラを実行するスレッド関数"""
    # 指定した時間ごとに処理を実行するようにスケジュール

    schedule.every(wait_time).seconds.do(xml_107_analyze)
    while not stop_capture:
        schedule.run_pending()
        time.sleep(1)

def rtp_107_processor_thread():
    """RTP-107パケットを処理するスレッド"""
    # 保存するパケットデータの数を制限
    max_packets = 5

    # RTPデータの保存用
    rtp_107_payload_data = []

    while not stop_capture:
        try:
            # タイムアウト付きでキューからパケット取得
            packet_data = rtp_107_queue.get(timeout=0.5)

            if packet_data:
                rtp_data = packet_data

                # パケットを保存
                rtp_107_packets.append(rtp_data)

                # RTPペイロードデータを抽出して保存
                if is_rtp_packet(rtp_data):
                    # RTPヘッダーサイズを計算
                    csrc_count = rtp_data[0] & 0x0F
                    header_size = 12 + (4 * csrc_count)

                    # 拡張ヘッダーがある場合
                    if (rtp_data[0] >> 4) & 0x01:
                        if len(rtp_data) >= header_size + 4:
                            ext_length = struct.unpack("!H", rtp_data[header_size + 2:header_size + 4])[0] * 4
                            header_size += 4 + ext_length

                    # ペイロードデータ抽出
                    if len(rtp_data) > header_size:
                        payload = rtp_data[header_size:]
                        rtp_107_payload_data.append(payload)

                # 最大パケット数を超えたら古いものを削除
                if len(rtp_107_packets) > max_packets:
                    rtp_107_packets.pop(0)
                    if rtp_107_payload_data:
                        rtp_107_payload_data.pop(0)

                # パケット数を表示
                if len(rtp_107_packets) % 10 == 0:  # 10パケットごとに表示
                    print("=====")
                    print(f"  [情報] 現在 {len(rtp_107_packets)} 個のRTP-107パケットを保持中")
                    print("=====")

        except queue.Empty:
            continue
        except Exception as e:
            print(f"RTP-107処理エラー: {e}")

    # キャプチャ終了時、パケットを保存するか確認
    if rtp_107_packets:
        try:
            # パケット保存の確認
            save = input(
                f"\n{len(rtp_107_packets)} 個のRTP-107パケットをファイルに保存しますか？ (y=PCAP/r=RAW/n=保存しない): ")
            if save.lower() == 'y':
                # PCAPファイルとして保存
                filename = f"rtp_107_packets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
                wrpcap(filename, rtp_107_packets)
                print(f"パケットを {filename} に保存しました")

            elif save.lower() == 'r' and rtp_107_payload_data:
                # RTPペイロードを連結してRAWファイルとして保存
                raw_filename = f"rtp_107_payload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.raw"
                with open(raw_filename, 'wb') as f:
                    for payload in rtp_107_payload_data:
                        f.write(payload)
                print(
                    f"RTP-107ペイロードデータを {raw_filename} に保存しました ({sum(len(p) for p in rtp_107_payload_data)} バイト)")

                # メタデータファイルも保存
                meta_filename = f"rtp_107_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(meta_filename, 'w') as f:
                    f.write(f"RTP-107パケット数: {len(rtp_107_packets)}\n")
                    f.write(f"総ペイロードサイズ: {sum(len(p) for p in rtp_107_payload_data)} バイト\n")
                    f.write(
                        f"平均ペイロードサイズ: {sum(len(p) for p in rtp_107_payload_data) / len(rtp_107_payload_data):.2f} バイト\n")
                    f.write(f"最小ペイロードサイズ: {min(len(p) for p in rtp_107_payload_data)} バイト\n")
                    f.write(f"最大ペイロードサイズ: {max(len(p) for p in rtp_107_payload_data)} バイト\n")
                    f.write(f"キャプチャ日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                print(f"メタデータを {meta_filename} に保存しました")

        except Exception as e:
            print(f"ファイル保存エラー: {e}")


def packet_display_thread():
    """パケット表示スレッド"""
    while not stop_capture:
        try:
            # タイムアウト付きでキューからパケット取得
            packet = packet_queue.get(timeout=0.5)
            # ここでパケットの詳細解析や保存処理を追加可能
        except queue.Empty:
            continue
        except:
            break


def get_all_interfaces():
    """システムの全ネットワークインターフェース名を取得"""
    return netifaces.interfaces()


def get_interface_ip(interface):
    """指定されたインターフェースのIPアドレスを取得"""
    try:
        if netifaces.AF_INET in netifaces.ifaddresses(interface):
            return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except:
        pass
    return None


def get_all_local_ips():
    """システムの全ネットワークインターフェースのIPアドレスを取得"""
    ips = []
    interfaces = {}
    for interface in netifaces.interfaces():
        ip = get_interface_ip(interface)
        if ip:
            ips.append(ip)
            interfaces[ip] = interface
    return ips, interfaces

def get_all_mac():
    macs = {}
    for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            mac = addrs.get(netifaces.AF_LINK)
            if mac:
                    macs[iface] = mac[0]['addr']
    return macs


def extract_server_ip(rtsp_url):
    """RTSP URLからサーバーIPアドレスを抽出する"""
    match = re.search(r'rtsp://([^:/]+)', rtsp_url)
    if match:
        server = match.group(1)
        try:
            # ホスト名の場合はIPアドレスに変換
            return socket.gethostbyname(server)
        except:
            pass
    return None


def select_capture_interface():
    """キャプチャに使用するインターフェースを選択する"""
    local_ips, ip_to_interface = get_all_local_ips()

    print("検出されたネットワークインターフェース:")
    for ip in local_ips:
        print(f"IP: {ip}, インターフェース: {ip_to_interface[ip]}")

    print("\nどのインターフェースを使用しますか？")
    all_interfaces = get_all_interfaces()
    for i, iface in enumerate(all_interfaces, 1):
        ip = get_interface_ip(iface) or "IP未設定"
        print(f"{i}. {iface} ({ip})")

    try:
        iface_choice = int(input("\n番号を入力: ")) - 1
        if 0 <= iface_choice < len(all_interfaces):
            selected_interface = all_interfaces[iface_choice]
            return selected_interface
        else:
            print("無効な選択です")
            return None
    except ValueError:
        print("数値を入力してください")
        return None


def start_packet_capture(server_ip, interface):
    """パケットキャプチャスレッドを開始"""
    global stop_capture
    stop_capture = False

    # RTSPとRTPパケットをキャプチャするフィルタ
    # RTSPは通常TCP/554、RTPはUDPの様々なポートを使用、TCP上のRTPも含む
    filter_str = f"host {server_ip} and (tcp port 554 or udp)"

    #print(f"\nフィルタ: {filter_str}")
    #print(f"インターフェース: {interface}")
    #print("パケットキャプチャを開始します...")
    #print("特に DynamicRTP-Type-107 パケットを監視しています...")
    #print("TCP上のRTP (インターリーブドモード) も検出します...")

    #mqtt_worker = threading.Thread(target=mqtt_thread, daemon=True)
    #mqtt_worker.start()

    # キャプチャスレッド
    capture_thread = threading.Thread(
        target=lambda: sniff(
            filter=filter_str,
            prn=packet_callback,
            store=0,
            iface=interface,
            stop_filter=lambda _: stop_capture
        )
    )
    capture_thread.daemon = True
    capture_thread.start()

    # 表示スレッド
    display_thread = threading.Thread(target=packet_display_thread)
    display_thread.daemon = True
    display_thread.start()

    # RTP-107処理スレッド
    rtp_107_thread = threading.Thread(target=rtp_107_processor_thread)
    rtp_107_thread.daemon = True
    rtp_107_thread.start()

    #定期実行するやつ
    scheduler_thread = threading.Thread(target=scheduler_exec)
    scheduler_thread.daemon = True
    scheduler_thread.start()



    return capture_thread, display_thread, rtp_107_thread, scheduler_thread


def run_video_display(rtsp_url, capture_thread, threads):
    global rtp_107_packets
    global capture_queue
    """映像表示を実行する関数"""
    # OpenCVでRTSPストリームを開く
    print(f"RTSPストリームに接続: {rtsp_url}")
    try:
        # GStreamerバックエンドを使用するオプション
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_GSTREAMER)

        # GStreamerが利用できない場合のフォールバック
        if not cap.isOpened():
            #print("GStreamerバックエンドでの接続に失敗しました。標準バックエンドを試行します...")
            cap = cv2.VideoCapture(rtsp_url)
    except Exception as e:
        print(f"接続エラー: {e}")
        cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("RTSPストリームを開けませんでした")
        global stop_capture
        stop_capture = True
        capture_thread.join(timeout=1)
        return

    # フレームサイズとFPSを取得
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"動画サイズ: {width}x{height}, FPS: {fps}")

    # ウィンドウ表示
    #cv2.namedWindow('RTSP Stream', cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("フレーム取得失敗")
                break

            with frame_buffer:
                capture_queue.append(frame)

            # 現在のタイムスタンプを表示
            #cv2.putText(
            #    frame,
            #    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            #    (15, 50),
            #    cv2.FONT_HERSHEY_SIMPLEX,
            #    0.5,
            #    (0, 255, 0),
            #    1
            #)

            # RTP-107パケットカウントを表示
            #rtp_107_count = rtp_107_queue.qsize()
            #cv2.putText(
            #    frame,
            #    f"metadata: {len(rtp_107_packets)}",
            #    (10, 70),
            #    cv2.FONT_HERSHEY_SIMPLEX,
            #    0.5,
            #    (0, 255, 255),
            #    2
            #)

            #cv2.imshow('RTSP Stream', frame)

            # ESCキーで終了
            #key = cv2.waitKey(1) & 0xFF
            #if key == 27:  # ESCキー
            #    break
    except KeyboardInterrupt:
        print("\n中断されました")
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        # リソース解放
        cap.release()
        #cv2.destroyAllWindows()


def mqtt_connect(config):
    global mqtt_client_obj
    client = mqtt.Client()

    client.username_pw_set(config[2], config[3])
    connect_result = {"rc" : None}

    def on_connect(client, userdata, flags, rc):
        connect_result["rc"] = rc
        print(f"[MQTT] Connected with result code {rc}")

    def on_disconnect(client, userdata, rc):
        connect_result["rc"] = rc
        print(f"[MQTT] Disconnected. rc={rc}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(str(config[0]), int(config[1]))
    client.loop_start()
    mqtt_client_obj = client

    return client

def mqtt_thread(config):
    client = mqtt_connect(config)


def main():
    global stop_capture
    global mac_address

    mqtt_info = [broker_ip, mqtt_port, mqtt_user, mqtt_password]

    #client = mqtt_connect(broker_ip, mqtt_port, mqtt_user, mqtt_password, client_id, topic)

    mqtt_worker = threading.Thread(target=mqtt_thread, args=(mqtt_info,))
    mqtt_worker.daemon = True
    mqtt_worker.start()

    #time.sleep(10)
    #result = mqtt_client_obj.publish(topic, "test message.")
    #print(result)
    #time.sleep(10)
    #exit()
    #parser = argparse.ArgumentParser(description='RTSPストリームビューアとパケットキャプチャ (RTP-107検出機能付き)')
    #parser.add_argument('--url', '-u', help='RTSP URL', default=f"rtsp://{user}:{password}@{server_ip}/ONVIF/MediaInput?profile=def_profile4")
    #parser.add_argument('--no-video', '-n', action='store_true', help='映像表示を無効化（パケットキャプチャのみ）')
    #args = parser.parse_args()

    # RTSP URLの入力
    #rtsp_url = args.url
    rtsp_url = url.format(user=user,password=password,server_ip=server_ip)


    # キャプチャインターフェースを選択
    #interface = select_capture_interface()
    interface = get_all_interfaces()[0]
    print(interface)
    mac_address = get_all_mac()[interface]

    print(name)
    if not interface:
        print("インターフェースが選択されていません。終了します。")
        return

    # パケットキャプチャ開始
    threads = start_packet_capture(server_ip, interface)
    capture_thread = threads[0]

    try:
        # 映像表示を実行
        run_video_display(rtsp_url, capture_thread, threads)
    finally:
        # 終了処理
        stop_capture = True
        for t in threads:
            t.join(timeout=3)
        print("終了しました")

if __name__ == "__main__":
    # このスクリプトは管理者/root権限が必要
    #print("RTSP ストリームビューア & RTP-107パケットキャプチャツール (TCP/UDP対応)")
    main()
