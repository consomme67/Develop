import requests
from datetime import datetime, timedelta
import pytz
import subprocess
import json

def get_json_data(url):
    try:
        response = requests.get(url)
        # ステータスコードが200 OKの場合のみ処理を続行
        if response.status_code == 200:
            # JSONデータを取得
            json_data = response.json()
            return json_data
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# APIのURL
api_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/380000.json"

# JSONデータを取得し、変数に格納
json_data = get_json_data(api_url)

# JSONデータが取得できた場合の処理
if json_data:
    # ここでJSON-Aとしての処理を実行
    # 例えば、JSONデータを利用して何らかの処理を行うなど
    print("JSON data successfully retrieved.")
    #print(json_data)
else:
    print("Failed to retrieve JSON data.")
    exit()

print("==================")

def get_data(json_data):
    areas = []
    weathers = []
    winds = []
    waves = []
    time_weathers = []
    for data in json_data[0]['timeSeries'][0]['timeDefines']:
            time_weathers.append(data)
    for i in range(3):
        areas.append(json_data[0]['timeSeries'][0]['areas'][i]['area']['name'])
        #print(len(areas))
        for data in json_data[0]['timeSeries'][0]['areas'][i]['weathers']:
            weathers.append(data)
        for data in json_data[0]['timeSeries'][0]['areas'][i]['winds']:
            winds.append(data)
        for data in json_data[0]['timeSeries'][0]['areas'][i]['waves']:
            waves.append(data)
    for j in range(len(weathers)):
        #print(len(weathers))
        #print(time_weathers[j])
        #time_weathers[j] = convert_to_timezone(time_weathers[j], 'Asia/Tokyo')
        weathers[j] = weathers[j].replace('\u3000', ' ')
        winds[j] = winds[j].replace('\u3000', ' ')
        waves[j] = waves[j].replace('\u3000', ' ')
    for k in range(len(time_weathers)):
        time_weathers[k] = convert_to_timezone(time_weathers[k], 'Asia/Tokyo')
    return time_weathers,areas,weathers,winds,waves


def convert_to_timezone(time_string, target_timezone):
    # 入力された時刻文字列をdatetimeオブジェクトに変換
    local_time = datetime.fromisoformat(time_string)

    # タイムゾーンを設定
    target_tz = pytz.timezone(target_timezone)

    # ターゲットタイムゾーンに変換してUTC時刻をISO 8601形式の文字列に変換して返す
    return local_time.replace(tzinfo=target_tz).isoformat()

def extract_data(json_data):
    try:
        result_data = get_data(json_data)
        print(result_data)

        # TimeDefines、areas>area>name、areas>weathersを取得
        #first_time_define = convert_to_utc(first_time_series.get('timeDefines', [])[0])
        # 現在のUTC時刻を取得
        current_utc_time = datetime.utcnow().replace(microsecond=0).isoformat()

        # UTCをJSTに変換
        first_time_define = convert_to_timezone(current_utc_time, 'Asia/Tokyo')

        current_jst_time = convert_to_timezone(current_utc_time, 'Asia/Tokyo')
        

        # 新しいJSONを作成
        formatted_json = {
            "ai_model": {"type": "Text", "value": "today_weather"},
            "asset_ID": {"type": "Text", "value": "hackathon-asset010"},
            "asset_name": {"type": "Text", "value": "おしらせチャンネルデータアセットxxxx"},
            "dateLastValueReported": {"type": "Text", "value": current_jst_time},
            #"id": "jp.ehime.hackathon.today_weather.hackathon-asset010.asset-001",
            "PublishingOffice": {"type": "text", "value": json_data[0]["publishingOffice"]},
            "TimeDefines": {"type": "text", "value": [result_data[0][0],result_data[0][1],result_data[0][2]]},
            "Areas": {"type": "text", "value": {"area01":result_data[1][0],"area02":result_data[1][1],"area03":result_data[1][2]}},
            "Weather_area01": {"type": "text", "value": [result_data[2][0],result_data[2][1],result_data[2][2]]},
            "Winds_area01": {"type": "text", "value": [result_data[3][0],result_data[3][1],result_data[3][2]]},
            "Waves_area01": {"type": "text", "value": [result_data[4][0],result_data[4][1],result_data[4][2]]},
            "Weather_area02": {"type": "text", "value": [result_data[2][3],result_data[2][4],result_data[2][5]]},
            "Winds_area02": {"type": "text", "value": [result_data[3][3],result_data[3][4],result_data[3][5]]},
            "Waves_area02": {"type": "text", "value": [result_data[4][3],result_data[4][4],result_data[4][5]]},
            "Weather_area03": {"type": "text", "value": [result_data[2][6],result_data[2][7],result_data[2][8]]},
            "Winds_area03": {"type": "text", "value": [result_data[3][6],result_data[3][7],result_data[3][8]]},
            "Waves_area03": {"type": "text", "value": [result_data[4][6],result_data[4][7],result_data[4][8]]},
            "use_case_ID": {"type": "Text", "value": "oshiraseCH"},
            "use_case_name": {"type": "Text", "value": "気象庁_天気予報"},
        }


        return formatted_json
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

formatted_json = extract_data(json_data)
print(json.dumps(extract_data(json_data), indent=2, ensure_ascii=False))
#format_json=extract_data(json_data)
# JSONをPOSTするためのcurlコマンドを組み立てて実行
url = '''http://10.2.1.175:1026/v2/entities/jp.ehime.hackathon.today_weather.hackathon-asset010.asset-001/attrs'''  # 実際のエンドポイントに変更
#curl_command = f'curl -X POST -H "Content-Type: application/json" -d \'{json.dumps(formatted_json, ensure_ascii=False)}\' {url}'


print(url)
print("===")
#print(curl_command)

try:
    #subprocess.run(curl_command, shell=True, check=True)
    print("JSONをPOSTしました。")
except subprocess.CalledProcessError as e:
    print(f"JSONのPOST中にエラーが発生しました。エラーコード: {e.returncode}")
    print(e.stderr.decode('utf-8'))

