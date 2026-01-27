import requests
import json
import configparser
import os
from string import Template
from datetime import datetime, timezone, timedelta

#デバッグ用
debug = False


class CrowdLevel:
	def __init__(self, place: str, point: str, name: str, raw_json=None, ptr=3):
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


	def write(self):
		try:
			with open("template.json", "r") as f:
				temp = f.read()

			self.write_data = Template(temp)
			filled = self.write_data.safe_substitute()

		except Exception as e:
			print(e)
		return self

	def get_Time(self):
		jst = timezone(timedelta(hours=9))
		now_jst = datetime.now(jst)
		dt_jst = now_jst.strftime("%Y-%m-%dT%H:%M:%S+09:00")

		return dt_jst

	def save(self, out_dir):
		os.makedirs(out_dir, exist_ok = True)
		out_path = out_dir + f'{self.name}.txt'
		with open(out_path, mode="w") as f:
			f.write(json.dumps(self.write_data, ensure_ascii=False, indent=2))
		return self


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

	try :
		raw_data = requests.get(url, timeout = 10)
		raw_data.raise_for_status()

		raw_json = raw_data.json()
		error = None
	except Exception as e :
		print(e)
		exit()

	#kaku titen gotoni syori
	for i in observePoints:
#		print(f'{i} ==> {observePoints[i]} ===> {observeNames[i]}')
		if i in pathToReaches:

			cl = CrowdLevel(i, observePoints[i], observeNames[i], raw_json, int(pathToReaches[i]))
		else :
			cl = CrowdLevel(i, observePoints[i], observeNames[i], raw_json)

		if debug:
			cl.debug_mode()
		cl.format()
		cl.write()

if __name__ == "__main__":
	main()
