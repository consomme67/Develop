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
    print(json_data)
else:
    print("Failed to retrieve JSON data.")
    exit()

print("==================")



def convert_to_timezone(time_string, target_timezone):
    # 入力された時刻文字列をdatetimeオブジェクトに変換
    local_time = datetime.fromisoformat(time_string)

    # タイムゾーンを設定
    target_tz = pytz.timezone(target_timezone)

    # ターゲットタイムゾーンに変換してUTC時刻をISO 8601形式の文字列に変換して返す
    return local_time.replace(tzinfo=target_tz).isoformat()
def extract_data(json_data):
    try:
        # timeSeriesの1つ目の要素を取得
        first_time_series = json_data[0]['timeSeries'][0]

        # TimeDefines、areas>area>name、areas>weathersを取得
        #first_time_define = convert_to_utc(first_time_series.get('timeDefines', [])[0])
        # 現在のUTC時刻を取得
        current_utc_time = datetime.utcnow().replace(microsecond=0).isoformat()

        # UTCをJSTに変換
        first_time_define = convert_to_timezone(current_utc_time, 'Asia/Tokyo')

        #time_define = first_time_define[:-6]
        time_define = first_time_series.get('timeDefines',[])[0]
        area_name = first_time_series['areas'][0]['area']['name']
        weathers = first_time_series['areas'][0]['weathers'][0]

        current_jst_time = convert_to_timezone(current_utc_time, 'Asia/Tokyo')
        cleaned_weather = weathers.replace('\u3000', ' ')

        print(time_define)
        # 新しいJSONを作成
        """
        new_json = {
            'TimeDefines': time_define,
            'AreaName': area_name,
            'Weathers': weathers
        }
        """
        formatted_json = {
            "ai_model": {"type": "Text", "value": "today_weather"},
            "camera_ID": {"type": "Text", "value": "hackathon-asset010"},
            "camera_name": {"type": "Text", "value": "ハッカソン用アセット010"},
            "dateLastValueReported": {"type": "Text", "value": current_jst_time},
            #"id": "jp.ehime.hackathon.today_weather.hackathon-asset010.asset-001",
            "TimeDefine": {"type": "text", "value": convert_to_timezone(time_define, 'Asia/Tokyo')},
            "Areaname": {"type": "text", "value": area_name},
            "Weather": {"type": "text", "value": cleaned_weather},
            #"type": "today_weather",
            "use_case_ID": {"type": "Text", "value": "hackathon"},
            "use_case_name": {"type": "Text", "value": "ハッカソン-天気（中予）"},
        }


        return formatted_json
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
formatted_json = extract_data(json_data)
#print(json.dumps(extract_data(json_data), indent=2, ensure_ascii=False))
format_json=extract_data(json_data)
# JSONをPOSTするためのcurlコマンドを組み立てて実行
url = '''http://10.2.1.175:1026/v2/entities/jp.ehime.hackathon.today_weather.hackathon-asset010.asset-001/attrs'''  # 実際のエンドポイントに変更
curl_command = f'curl -X POST -H "Content-Type: application/json" -d \'{json.dumps(formatted_json, ensure_ascii=False)}\' {url}'


print(url)
print("===")
print(curl_command)

try:
    subprocess.run(curl_command, shell=True, check=True)
    print("JSONをPOSTしました。")
except subprocess.CalledProcessError as e:
    print(f"JSONのPOST中にエラーが発生しました。エラーコード: {e.returncode}")
    print(e.stderr.decode('utf-8'))

