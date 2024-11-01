import csv
from crate import client

# CrateDBに接続
connection = client.connect("http://10.2.1.176:4200")

# クエリを実行
cursor = connection.cursor()
cursor.execute('SELECT "datelastvaluereported","camera_id","camera_name","line1_in_total","line1_out_total" FROM "doc"."etipro-motion-detection" where "time_index">=1722664800000 and "time_index"<=1722693600000 and "camera_id"=\'icam004\' order by "datelastvaluereported" LIMIT 25200;')

# 結果をCSVファイルに書き込む
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # カラム名を書き込む
    writer.writerow([i[0] for i in cursor.description])
    # 行データを書き込む
    writer.writerows(cursor.fetchall())