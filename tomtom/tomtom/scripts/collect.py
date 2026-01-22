import requests
import json
import configparser
import os
from collections import deque
from datetime import datetime, timezone, timedelta


class CrowdLevel:
	def __init__(self, place: str, point: str, raw_json=None, ptr=3):
		self.place = place
		self.point = point
		self.ptr = int(ptr)
		self.raw_json = raw_json
		self.write_data = None

	def test(self):
		print(len(self.path))
		#print(len(self.raw_json))
		#print(len(self.raw_json["detailedSegments"]))

		#print(self.format_data())

	def format(self):
		#print(self.place)
		list = []
		self.path = []

		for i in self.raw_json["detailedSegments"]:
			list.append(i["segmentIdStr"])
			if self.point == i["segmentIdStr"]:
				print(f'{self.place} : OK!')

				idx = list.index(self.point)
				print(f'{type(self.ptr)} : {self.ptr}')
				for k in range(self.ptr):
					idx = idx-1
					self.path.append(self.raw_json["detailedSegments"][idx])
				print(self.path)
				return self

	def write(self):
		try:
			self.raw_json = format_data(self.raw_json)
			print(self.raw_json)
			self.write_data = {
				"asset_ID" : {
					"type" : "Text",
					"value" : self.raw_json.get("routeId")
				},
				"datetime" : {
					"type" : "Text",
					"value" : self.raw_json.get("createdAt")
				},
				"status" : self.raw_json.get("routeStatus"),
				"passable" : self.raw_json.get("passable"),
				"delaytime" : self.raw_json.get("delayTime")
			}
		except Exception as e:
			print(e)
		return self

	def save(self, out_dir):
		os.makedirs(out_dir, exist_ok = True)
		out_path = out_dir + f'{self.name}.txt'
		with open(out_path, mode="w") as f:
			f.write(json.dumps(self.write_data, ensure_ascii=False, indent=2))
		return self

	def get_Time(self):
		jst = timezone(timedelta(hours=9))
		now_jst = datetime.now(jst)
		dt_jst = now_jst.strftime("%Y-%m-%dT%H:%M:%S+09:00")

		return dt_jst


def load_config(path):
	config = configparser.ConfigParser(comment_prefixes=("#"))
	config.read(path, encoding='utf-8')
	return config

def main():
	config = load_config("config.ini")

	out_dir = config['Directory']['out_dir']
	url = config['APIurl']['url']
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
		if i in pathToReaches:
			cl = CrowdLevel(i, observePoints[i], raw_json, pathToReaches[i])
		else :
			cl = CrowdLevel(i, observePoints[i], raw_json)
		
		cl.format()
		cl.test()


	print(out_dir)
	print(url)

if __name__ == "__main__":
	main()
