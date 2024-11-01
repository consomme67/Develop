import json
import sys
from paho.mqtt import client as mqtt_client

# 設定ファイルを読み込む
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

# メッセージ受信時のコールバック関数
def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' from topic '{message.topic}'")
    data = json.loads(message.payload.decode())
    process_data(data)

# JSONデータ処理関数
def process_data(data):
    # JSONデータに基づいて処理を行う（ここでtest.pyを実行）
    
    # JSONデータから特定の値を抽出
    area1_current = data.get("Area1_Current", 0)
    area2_current = data.get("Area2_Current", 0)
    area3_current = data.get("Area3_Current", 0)
    area4_current = data.get("Area4_Current", 0)
    
    # カンマ区切りの文字列として整形
    formatted_string = f"{area1_current},{area2_current},{area3_current},{area4_current}"
    
    from subprocess import call
    call(["python", "lorawan-send.py", formatted_string])

# MQTTクライアント設定と接続
def run():
    config = load_config()
    client = mqtt_client.Client("PythonMQTTClient")
    client.on_message = on_message
    client.connect(config['broker'], config['port'])
    client.subscribe(config['topic'])
    client.loop_forever()  # 常駐してメッセージ待ち

if __name__ == "__main__":
    run()
