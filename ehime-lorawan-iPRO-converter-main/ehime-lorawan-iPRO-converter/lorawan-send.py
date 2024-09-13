import serial
import sys
import time

# 文字列をLoRaWANに送付するためHEX文字列に変換する


def string_to_hex(input_string):
    # 文字列をバイト列に変換
    bytes_string = input_string.encode('utf-8')
    # バイト列をHEX文字列に変換
    return bytes_string.hex()


def establish_connection(retry=3):
    # 通信確立
    while retry > 0:
        try:
            ser = serial.Serial('/dev/ttyS0', 115200, timeout=0.1)
            if ser.isOpen():
                print("Connection established.")
                return ser
            else:
                print("Failed to open serial port. Retrying...")
        except serial.SerialException as e:
            print(f"Serial connection failed: {e}")
            time.sleep(2)  # 2秒待機してから再試行
        retry -= 1
    print("Failed to establish connection. Exiting.")
    sys.exit(1)


def set_channel_plan_and_join(ser):
    ser.write(b"lorawan set_ch_plan AS923\r")
    time.sleep(10)  # コマンド応答を待つ
    response = ser.read_all().decode()
    print(f"Channel plan response: {response}")

    if "Ok" in response:
        ser.write(b"lorawan join otaa\r")
        time.sleep(10)  # OTAAによる接続が完了するまで待機
        ser.write(b"lorawan get_join_status\r")
        time.sleep(0.5)
        response = ser.read_all().decode()
        print(f"Join status response after join attempt: {response}")
        if not "unjoined" in response:
            print("Joined LoRaWAN successfully.")
            return True
        else:
            print("Failed to join LoRaWAN.")
            return False
    else:
        print("Failed to set channel plan.")
        return False


def check_and_join_lorawan(ser):
    ser.write(b"lorawan get_join_status\r")
    time.sleep(0.5)  # コマンド応答を待つ
    response = ser.read_all().decode()
    print(f"Join status response: {response}")

    if "not_joined" in response or "unjoined" in response or "0" in response:
        print("Not joined to LoRaWAN. Attempting to join...")
        if not set_channel_plan_and_join(ser):
            return False
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lorawan-send.py {文字列}")
        sys.exit(1)

    original_string = sys.argv[1]

    if len(original_string.encode('utf-8')) > 11:
        print("Error: The string must be 11 bytes or less in UTF-8 encoding.")
        sys.exit(1)

    hex_string = string_to_hex(original_string)
    ser = establish_connection()

    # データ送信
    serialCmd = f"lorawan tx ucnf 1 {hex_string}\r".encode()
    ser.write(serialCmd)
    time.sleep(0.5)  # コマンド応答を待つ
    response = ser.read_all().decode()
    print(f"TX response: {response}")

    if ">> not_joined" in response:
        if not check_and_join_lorawan(ser):
            ser.close()
            sys.exit(1)
        # 再送信
        ser.write(serialCmd)
        time.sleep(0.5)
        response = ser.read_all().decode()
        print(f"TX response after join: {response}")

    while True:
        L_ReceiveData = ser.readline()
        ReceiveData = L_ReceiveData.decode()

        DataLength = len(L_ReceiveData)

        if DataLength == 0:
            break
        else:
            print(ReceiveData)

    ser.close()
