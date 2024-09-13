# ehime-lorawan-iPRO-converter

愛媛CATV様向けLoRa WAN 実証実験要プログラム

i-PRO 混雑検知をLoRa WAN経由でデータ送信を行う。

LoRaWANでは、1回あたりの送信が11バイトと制限されているため、今回のデモアプリでは、11バイト以内に収まるよう、以下のデータをカンマ区切りで送付するのみとする。

- Area1_Current
- Area2_Current
- Area3_Current
- Area4_Current

それぞれ0-40の2桁となるため、`00,00,00,00`の最大11バイトとなる。


## 使用方法

```
$ python mqtt-client.py
```

## 設定

### config.json
MQTTの接続情報を記載する(Raspberry pi 内にブローカーを別途立てることで対応するため素のまま一旦は構築する)

```
{
    "broker": "localhost",
    "port": 1883,
    "topic": "i-PRO/NetworkCamera/App/AIOccupancyDetectionApp"
}
```


## プログラムの自動起動

mqtt-client.pyをサービス化し自動起動・停止時のリカバリを行う設定を行います。

### 使用手順

   - **サービスのインストール**
     ```sh
     ./autoboot_service.sh install
     ```
     - `mqtt-client.service`ファイルを`/etc/systemd/system`にコピーし、サービスを有効化して開始します。

   - **サービスのアンインストール**
     ```sh
     ./autoboot_service.sh uninstall
     ```
     - サービスを停止し、無効化して、サービスファイルを削除します。

   - **サービス自動起動の有効化**
     ```sh
     ./autoboot_service.sh enable
     ```

   - **サービス自動起動の無効化**
     ```sh
     ./autoboot_service.sh disable
     ```

## microSDのリードオンリー化

このスクリプトは、Raspberry PiのSDカードを延命化するためリードオンリーモードに切り替えたり、リード/ライトモードに戻したりします。

### 使用手順

   - **リードオンリー化を有効化**
     ```sh
     ./readonly_microsd.sh enable
     ```
     - ルートファイルシステムをリードオンリーモードに切り替えます。

   - **リードオンリー化を無効化**
     ```sh
     ./readonly_microsd.sh disable
     ```
     - ルートファイルシステムをリード/ライトモードに戻します。