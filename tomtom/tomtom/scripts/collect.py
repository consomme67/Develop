import requests
import json
import configparser
import os
from string import Template
from datetime import datetime, timezone, timedelta
import paho.mqtt.client as mqtt

#デバッグ用
debug = False


class CrowdLevel:
	def __init__(self, client, place: str, point: str, name: str, raw_json=None, ptr=3):
		self.client = client
		self.place = place
		self.name = name
		self.point = point
		self.ptr = ptr
		self.raw_json = raw_json
		self.write_data = None

	def debug_mode(self):
		for key, value in self.__dict__.items():
			print("===============")
			print(f"{key}: {value}")
			print("===============")

	def format(self):
		list = []
		self.segments = []

		for i in self.raw_json["detailedSegments"]:
			#監視地点まで各セグメントをリスト化していく
			list.append(i["segmentIdStr"])

			#監視地点から設定した取得セグメントの情報をまとめる
			if self.point == i["segmentIdStr"]:
				idx = list.index(self.point)
				for k in range(self.ptr):
					data = {"segment_no" : k+1,
							"segment_id" : self.raw_json["detailedSegments"][idx]["segmentIdStr"],
							"segment_length" : self.raw_json["detailedSegments"][idx]["segmentLength"],
							"current_speed" : self.raw_json["detailedSegments"][idx]["currentSpeed"],
							}
					self.segments.append(data)
					idx = idx - 1

				return self


	def send(self):
		try:
			with open("template.json", "r") as f:
				temp = f.read()
			#data = json.loads(temp)

			self.get_Time()
			place = self.place + "001"
			name = self.name + "001"
			self.write_data = Template(temp)

			traffic_states = json.dumps(self.segments)

			#print(traffic_states)
			filled = self.write_data.safe_substitute(asset_ID=place,
													 asset_name=name,
													 datetime=self.dt_jst,
													 data=traffic_states)

			obj = json.dumps(filled)
			tmp = json.loads(filled)

			tenant = tmp["data_value5"]
			driver = tmp["data_value2"]
			obj = json.dumps(tmp)
			topic = f'jp.ehime/{tenant}/{driver}'
			self.client.publish(topic=topic, qos=0, payload=obj)

		except Exception as e:
			print(e)
		return self

	def get_Time(self):
		jst = timezone(timedelta(hours=9))
		now_jst = datetime.now(jst)
		self.dt_jst = now_jst.strftime("%Y-%m-%dT%H:%M:%S+09:00")

		return self

	def save(self, out_dir):
		os.makedirs(out_dir, exist_ok = True)
		out_path = out_dir + f'{self.name}.txt'
		with open(out_path, mode="w") as f:
			f.write(json.dumps(self.write_data, ensure_ascii=False, indent=2))
		return self

def connect_mqtt(mqttuser):
	client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
	user = mqttuser["user"]
	password = mqttuser["password"]
	host = mqttuser["host"]

	client.username_pw_set(
		username=user,
		password=password
	)

	client.connect(host, 1883, 60)
	client.loop_start()
	return client


def load_config(path):
	config = configparser.ConfigParser(comment_prefixes=("#"))
	config.read(path, encoding='utf-8')
	return config

def main():
	config = load_config("config.ini")

	out_dir = config['Directory']['out_dir']
	url = config['APIurl']['url']
	observeNames = config["ObserveNames"]
	observePoints = config["ObservePoints"]
	pathToReaches = config["PathToReaches"]
	mqttuser = config['MqttUser']

	try :
		raw_data = requests.get(url, timeout = 10)
		raw_data.raise_for_status()

		raw_json = raw_data.json()
		error = None
	except Exception as e :
		print(e)
		exit()

	try :
		mqtt_client = connect_mqtt(mqttuser)


		#kaku titen gotoni syori
		for i in observePoints:
	#		print(f'{i} ==> {observePoints[i]} ===> {observeNames[i]}')
			if i in pathToReaches:

				cl = CrowdLevel(mqtt_client, i, observePoints[i], observeNames[i], raw_json, int(pathToReaches[i]))
			else :
				cl = CrowdLevel(mqtt_client, i, observePoints[i], observeNames[i], raw_json)

			if debug:
				cl.debug_mode()
			cl.format()
			cl.send()
		mqtt_client.loop_stop()
		mqtt_client.disconnect()

	except Exception as e:
		print(e)

		mqtt_client.loop_stop()
		mqtt_client.disconnect()

if __name__ == "__main__":
	main()
