import paho.mqtt.client as mqtt  # MQTTのライブラリをインポート
import datetime
import json

sub_broker_IP = "10.0.36.42"
sub_broker_Port = 1883
sub_broker_User = "aidai-demo01"
sub_broker_Pass = "7eTESRYc"

pub_broker_IP = "10.2.1.144" #Fiware想定
pub_broker_Port = 1883
pub_broker_User = ""
pub_broker_Pass = ""

id = {
    "d42dc52498f8":"テスト"
}

def on_connect(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))  # 接続できた旨表示
    client.subscribe("i-PRO/NetworkCamera/App/AIOccupancyDetectionApp")  # subするトピックを設定


# ブローカーが切断したときの処理
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    # msg.topicにトピック名が，msg.payloadに届いたデータ本体が入っている
    #print("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))

    #filename = msg.topic.replace("/", "_") + ".txt"

    dmesse = msg.payload.decode()
    #print(type(mes))
    message = json.loads(dmesse)
    #print(type(message))
    #print(type(message.get("CameraMACaddress")))
    #print(id.get("d42dc52498f8"))
    #print(id.get(message.get("CameraMACaddress")))
    if id.get(message.get("CameraMACaddress")):

        filename = id.get(message.get("CameraMACaddress")) + ".txt"
        #print(filename)
        getdate = datetime.datetime.strptime(message.get("Time"), "%Y%m%d%H%M%S") + datetime.timedelta(hours=9)
        exp_date = getdate.strftime('%Y%m%d%H%M%S')

        #print(exp_date)

        exp_all = message.get('ALL_Current')
        exp_area1 = message.get('Area1_Current')
        exp_area2 = message.get('Area2_Current')
        exp_area3 = message.get('Area3_Current')
        exp_area4 = message.get('Area4_Current')

        content = "Time : " + exp_date + "\n" +\
                   "ALL : " + exp_all + "\n" +\
            "Area1 : " + exp_area1 + "\n" +\
                  "Area2 : " + exp_area2 + "\n" +\
                  "Area3 : " + exp_area3 + "\n" +\
                  "Area4 : " + exp_area4 + "\n"


        with open("../"+filename, mode="w") as f:
            f.write(content)
            f.close()
"""
    print('ALL:' + exp_all)
    print('area1:' + exp_area1)
    print('area2:' + exp_area2)
    print('area3:' + exp_area3)
    print('area4:' + exp_area4)
"""
def pub_massage(msg):
    print(str(msg.payload) + "-->これをそのまま or バイナリ復号して送信")

# MQTTの接続設定
client = mqtt.Client()  # クラスのインスタンス(実体)の作成
client.username_pw_set(sub_broker_User, sub_broker_Pass)
client.on_connect = on_connect  # 接続時のコールバック関数を登録
client.on_disconnect = on_disconnect  # 切断時のコールバックを登録
client.on_message = on_message  # メッセージ到着時のコールバック

client.connect(sub_broker_IP, sub_broker_Port)

#print("===")
#print(client.on_message)

client.loop_forever()




