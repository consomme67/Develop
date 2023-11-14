import os
import sys
import psutil

def find_and_terminate_process_by_script_name(script_name):
    # カスタムの環境変数を設定してPythonスクリプトを実行
    os.environ['MY_CUSTOM_SCRIPT'] = script_name
    python_path = sys.executable
    process = psutil.Popen([python_path, 'stop.py'])

    # Pythonスクリプトを実行しているプロセスを検索
    for proc in psutil.process_iter(['pid', 'environ']):
        if proc.info['environ'] and 'MY_CUSTOM_SCRIPT' in proc.info['environ']:
            # カスタムの環境変数に基づいてプロセスを特定
            if proc.info['environ']['MY_CUSTOM_SCRIPT'] == script_name:
                pid = proc.info['pid']
                print(f"スクリプト名 {script_name} のプロセスが見つかりました (PID: {pid})。プロセスを終了します。")
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    print(f"プロセス {pid} を終了しました。")
                except psutil.NoSuchProcess:
                    print(f"プロセス {pid} が見つかりません。終了できませんでした。")
                break

if __name__ == "__main__":
    script_name_to_search = "stop.py"  # 検索したいスクリプト名をここに入力
    find_and_terminate_process_by_script_name(script_name_to_search)