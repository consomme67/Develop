"""
サイボウズのカスタムアプリ（システム開発受付）へ起票内容を収集・整理し、CSVにまとめる
CSVは社内のChatAIに取り込ませることでナレッジとして活用する。
"""



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
#import os
import csv

# ログイン情報
LOGIN_URL = "https://e-catv.cybozu.com/login"  # ログインページのURL
USERNAME = "h.kimura"  # ログインID（各自の環境に合わせて変更）
PASSWORD = "pU5j8ypT"  # パスワード（各自の環境に合わせて変更）


def setup_driver():
    """WebDriverの初期設定を行う関数"""
    options = webdriver.ChromeOptions()
    # ヘッドレスモードで実行する場合 (GUIなしでバックグラウンド実行)
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--window-size=1920,1080")  # ヘッドレスの場合、ウィンドウサイズ指定推奨
    options.add_argument("--incognito")  # シークレットモードで起動
    # options.add_argument("--disable-gpu") # Windowsでheadlessを使う場合に必要になることがある

    # WebDriverのサービスを設定
    service = Service()
    #driver = webdriver.Chrome(service=service)

    return webdriver.Chrome(service=service, options=options)
    #return webdriver.Chrome(service=service)


def clean_string_for_csv(value):
    """
    CSVセルに安全に格納するため、文字列から特定の文字を除去・置換する関数。
    Noneや非文字列が渡された場合も適切に処理します。
    """
    if value is None:
        return ""

    s = str(value)

    # 改行を半角スペースに置換
    s = s.replace("\n", " ")
    # カンマを削除
    s = s.replace(",", "")
    # 余分なスペースを除去 (前後のスペースは strip() で、途中の連続スペースは1つにまとめる)
    s = " ".join(s.split()).strip()

    return s

def login_to_cybozu(driver, username, password):
    """サイボウズへのログイン処理を行う関数"""
    print(f"ログインページにアクセス中: {LOGIN_URL}")
    driver.get(LOGIN_URL)

    try:
        # ログインID入力欄を特定し、入力
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(username)
        print("ユーザー名を入力しました。")

        # パスワード入力欄を特定し、入力
        driver.find_element(By.NAME, "password").send_keys(password)
        print("パスワードを入力しました。")

        # ログインボタンをクリック
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='ログイン']"))
        )
        login_button.click()
        print("ログインボタンをクリックしました。")

        # ログイン後のページが表示されるまで待機 (https://e-catv.cybozu.com/ が成功ページ)
        WebDriverWait(driver, 20).until(EC.url_to_be("https://e-catv.cybozu.com/"))
        print("ログイン成功！Cybozu.comのポータルページにアクセスできました。")
        print(f"現在のURL: {driver.current_url}")
        return True

    except TimeoutException:
        print("エラー: ログインページの要素が見つからないか、ログイン後のページへのリダイレクトがタイムアウトしました。")
        print(f"現在のURL: {driver.current_url}")
        driver.save_screenshot("login_timeout_screenshot.png")
        return False
    except Exception as e:
        print(f"エラー: ログイン処理中に予期せぬ問題が発生しました: {e}")
        print(f"現在のURL: {driver.current_url}")
        driver.save_screenshot("login_error_screenshot.png")
        return False


def navigate_to_workflow_list(driver):
    """Officeポータルからワークフロー一覧ページへの遷移を行う関数"""
    print("サイボウズOfficeへのリンクを探してクリックします。")
    try:
        # <a href="/o/" title="サイボウズ Office">...</a> の要素を探す
        office_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@title='サイボウズ Office' and @href='/o/']"))
        )
        office_link.click()
        print("サイボウズOfficeへのリンクをクリックしました。")

        # Officeのポータルページ（/o/）に遷移するまで待機
        WebDriverWait(driver, 15).until(EC.url_to_be("https://e-catv.cybozu.com/o/"))
        print("Cybozu Officeのポータルページにアクセス成功。")
        print(f"現在のURL: {driver.current_url}")

        # カスタムアプリ（ワークフロー）の一覧ページに直接URLでアクセス
        workflow_list_url = "https://e-catv.cybozu.com/o/ag.cgi?page=DBView&did=398"
        driver.get(workflow_list_url)
        print(f"カスタムアプリ（ワークフロー）一覧ページにアクセスしました: {workflow_list_url}")

        # ワークフロー一覧ページが表示されるまで待機
        WebDriverWait(driver, 20).until(EC.url_to_be(workflow_list_url))
        print("カスタムアプリ（ワークフロー）一覧ページにアクセス成功。")
        print(f"現在のURL: {driver.current_url}")

        on_the_way = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='未完了']"))
        )
        on_the_way.click()
        print("未完了ステータスへ移行")


        return True

    except TimeoutException:
        print("エラー: Officeへの遷移またはワークフロー一覧ページへのアクセスがタイムアウトしました。")
        print(f"現在のURL: {driver.current_url}")
        driver.save_screenshot("navigation_timeout_screenshot.png")
        return False
    except Exception as e:
        print(f"エラー: ワークフロー一覧ページへのナビゲーション中に予期せぬ問題が発生しました: {e}")
        print(f"現在のURL: {driver.current_url}")
        driver.save_screenshot("navigation_error_screenshot.png")
        return False


def extract_all_workflow_data_with_pagination(driver):
    """
    ワークフロー一覧ページから全てのデータを抽出し、ページネーションを処理する関数。
    """
    all_workflow_records = []
    page_num = 1
    #base_url = "https://e-catv.cybozu.com/o/"  # 相対パスを絶対パスにするためのベースURL

    while True:
        print(f"\n--- ページ {page_num} のワークフローデータを抽出中 ---")

        # ワークフロー一覧のテーブルが読み込まれるまで待機
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "DBView-db398-229")))
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#DBView-db398-229 tbody tr:has(td.dz_fontSmall)"))
            )
            print(f"ページ {page_num} のテーブルコンテンツが表示されました。")

        except TimeoutException:
            print(
                f"エラー: ページ {page_num} のワークフロー一覧のテーブルコンテンツが指定された時間内に読み込まれませんでした。")
            driver.save_screenshot(f"workflow_table_load_timeout_page_{page_num}.png")
            break  # タイムアウトしたらループを終了
        except Exception as e:
            print(
                f"エラー: ページ {page_num} のワークフロー一覧のテーブルコンテンツ待機中に予期せぬ問題が発生しました: {e}")
            driver.save_screenshot(f"workflow_table_load_error_page_{page_num}.png")
            break  # エラーが発生したらループを終了

        # 全てのワークフローの行 (<tr>) を取得
        workflow_rows = driver.find_elements(By.CSS_SELECTOR, "#DBView-db398-229 tbody tr")

        if not workflow_rows:
            print(f"ページ {page_num} でワークフローの行が見つかりませんでした。")
            if page_num == 1:  # 最初のページで何もなければ、本当にデータがない
                print("最初のページでレコードが見つかりませんでした。")
            break  # 行が見つからなければループを終了 (最終ページか、データがない場合)

        current_page_records = []
        # 各行のデータを抽出
        for i, row in enumerate(workflow_rows):
            try:
                record_id_element = row.find_element(By.CLASS_NAME, "record-value-number")
                record_id = record_id_element.text.strip() if record_id_element else None

                modify_time_element = row.find_element(By.CLASS_NAME, "record-value-modify-time")
                modify_time = modify_time_element.text.strip() if modify_time_element else None

                person_in_charge_element = row.find_element(By.CLASS_NAME, "record-value-1644")
                person_in_charge = person_in_charge_element.text.strip() if person_in_charge_element else None

                status_element = row.find_element(By.CLASS_NAME, "record-value-269")
                status = status_element.text.strip() if status_element else None

                title_element = row.find_element(By.CLASS_NAME, "record-value-4")
                title = title_element.text.strip() if title_element else None

                detail_link_element = row.find_element(By.XPATH, ".//a[img/@alt='依頼を閲覧する']")
                relative_detail_url = detail_link_element.get_attribute("href")

                #full_detail_url = base_url + relative_detail_url
                full_detail_url = relative_detail_url

                current_page_records.append({
                    "record_id": record_id,
                    "modify_time": modify_time,
                    "person_in_charge": person_in_charge,
                    "status": status,
                    "title": title,
                    "detail_url": full_detail_url
                })

            except NoSuchElementException as e:
                print(
                    f"警告: ページ {page_num} の行 {i} で必要な要素が見つかりませんでした。この行はスキップされます。詳細: {e}")
                print(f"問題の行HTML: {row.get_attribute('outerHTML')}")
            except Exception as e:
                print(f"エラー: ページ {page_num} の行 {i} の解析中に予期せぬ問題が発生しました: {e}")
                print(f"問題の行HTML: {row.get_attribute('outerHTML')}")

        all_workflow_records.extend(current_page_records)
        print(f"ページ {page_num} から {len(current_page_records)}件のレコードを抽出しました。")

        # --- 次のページへの遷移処理 ---
        try:
            # 「次の50件へ >>」ボタンを探す
            next_page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., '次の50件へ') and contains(., '>>')]"))
            )
            # クリックする前のURLを覚えておく
            current_url_before_click = driver.current_url
            next_page_button.click()
            print(f"ページ {page_num} の「次の50件へ >>」ボタンをクリックしました。")

            # ページのロードを待機
            # URLが変化するまで待つ。JavaScriptによる遷移なので、完全に新しいURLになることを期待。
            WebDriverWait(driver, 20).until(EC.url_changes(current_url_before_click))
            print(f"ページ {page_num + 1} に遷移しました。新しいURL: {driver.current_url}")

            page_num += 1
            # 少し待機して、ブラウザが完全に描画するのを助ける (オプション)
            time.sleep(1)

        except TimeoutException:
            print("「次の50件へ >>」ボタンが見つからないか、クリックできませんでした。最終ページに到達したと判断します。")
            break
        except Exception as e:
            print(f"エラー: ページネーション処理中に問題が発生しました: {e}")
            driver.save_screenshot(f"pagination_error_page_{page_num}.png")
            break  # エラーが発生したらループを終了

    return all_workflow_records


def extract_detail_data(driver, detail_url):
    """
    ワークフロー詳細ページからデータを抽出する関数。
    コメントの「すべて表示する」ボタンも処理する。
    """
    print(f"詳細ページにアクセス中: {detail_url}")
    driver.get(detail_url)

    detail_data = {}

    try:
        # ページが完全に読み込まれるまで待機
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.dz_viewRecordDefaultFieldValue"))
        )
        print("詳細ページのメインコンテンツが読み込まれました。")

        # --- 「すべて表示する」ボタンの処理 ---
        try:
            # ボタンを探す (テキストで特定)
            show_all_comments_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'すべて表示する')]"))
            )
            print("「すべて表示する」ボタンが見つかりました。クリックします。")

            # クリックする前のURLを覚えておく (ページの再読み込みを検出するため)
            current_url_before_click = driver.current_url
            show_all_comments_button.click()

            # ページの再読み込みを待機。URLが変わるか、同じURLでDOMが更新されるのを待つ。
            # 今回は href に URL が直接指定されているので、URL変化を待つのが確実。
            WebDriverWait(driver, 10).until(EC.url_changes(current_url_before_click))
            print("「すべて表示する」ボタンクリック後、ページが再読み込みされました。")

            # 再読み込み後もメインコンテンツがロードされるまで再度待機
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.dz_viewRecordDefaultFieldValue"))
            )
            print("再読み込み後の詳細ページのメインコンテンツが読み込まれました。")

        except TimeoutException:
            print(
                "「すべて表示する」ボタンは見つかりませんでした（またはクリックできませんでした）。すべてのコメントが既に表示されているか、コメントがない可能性があります。")
        except Exception as e:
            print(f"「すべて表示する」ボタン処理中にエラーが発生しました: {e}")
            # エラーが発生しても、その後のデータ抽出は試みる

        # --- 1. トップレベルのデータ と 2. その他のデータ ---
        # これらの抽出はボタンクリックの前後どちらでも構わないが、
        # ページ全体の再読み込みを考慮して、ボタンクリック後に再度抽出するのが確実。
        # 前回提案したコード部分をここに再配置（変更なし）
        try:
            detail_data["申請番号"] = driver.find_element(By.CSS_SELECTOR,
                                                          "table.dz_viewRecordDefaultFieldValue td.record-value-number").text.strip()
        except NoSuchElementException:
            detail_data["申請番号"] = None

        try:
            detail_data["申請日"] = driver.find_element(By.CSS_SELECTOR,
                                                        "table.dz_viewRecordDefaultFieldValue td.record-value-create-time").text.strip()
        except NoSuchElementException:
            detail_data["申請日"] = None

        try:
            detail_data["申請者"] = driver.find_element(By.CSS_SELECTOR,
                                                        "table.dz_viewRecordDefaultFieldValue td.record-value-creator").text.strip()
        except NoSuchElementException:
            detail_data["申請者"] = None

        try:
            text = driver.find_element(By.CSS_SELECTOR, "td.record-value-4").text.strip()
            detail_data["申請名"] = text.replace("\n", " ").replace(",", "")
        except NoSuchElementException:
            detail_data["申請名"] = None

        try:
            text = driver.find_element(By.CSS_SELECTOR, "td.record-value-5").text.strip()
            detail_data["申請内容"] = text.replace("\n", " ").replace(",", "")
        except NoSuchElementException:
            detail_data["申請内容"] = None

        try:
            detail_data["対応者"] = driver.find_element(By.CSS_SELECTOR, "td.record-value-8").text.strip()
        except NoSuchElementException:
            detail_data["対応者"] = None

        try:
            text = driver.find_element(By.CSS_SELECTOR, "td.record-value-950").text.strip()
            detail_data["対応内容"] = text.replace("\n", " ").replace(",", "")
        except NoSuchElementException:
            detail_data["対応内容"] = None

        # 添付資料の処理 (前回提案したコード部分をここに再配置)
        for i, field_id in enumerate([355, 356, 357]):
            try:
                attachment_td = driver.find_element(By.CSS_SELECTOR, f"td.record-value-{field_id}")
                attachment_links = attachment_td.find_elements(By.TAG_NAME, "a")

                if attachment_links:
                    files_info = []
                    for link in attachment_links:
                        text = link.text.strip()
                        file_name = text.replace("\n", " ").replace(",", "")
                        file_url = link.get_attribute("href")
                        files_info.append({"name": file_name, "url": file_url})
                    detail_data[f"添付資料{i + 1}"] = files_info
                else:
                    detail_data[f"添付資料{i + 1}"] = None
            except NoSuchElementException:
                detail_data[f"添付資料{i + 1}"] = None

        # --- 3. コメント履歴 ---
        # 「すべて表示する」ボタンクリック後にコメントを確実に取得
        comments_list = []
        try:
            comment_elements = driver.find_elements(By.CSS_SELECTOR,
                                                    "ol.vr_followList.notificationCommentList li.vr_followWrapper")
            if comment_elements:
                print(f"{len(comment_elements)}件のコメントが見つかりました。")

                for comment_el in comment_elements:
                    comment_info = {}
                    try: # もしNoがない（コメントではない）場合はスキップ
                        comment_info["number"] = comment_el.find_element(By.CSS_SELECTOR, "span.vr_followNo").text.strip()
                        comment_info["creator_name"] = comment_el.get_attribute("data-creator-name")  # data-属性から取得
                    except NoSuchElementException:
                        continue

                    # 日付の抽出
                    try:
                        comment_info["date"] = comment_el.find_element(By.CSS_SELECTOR, "span.vr_followTime").text.strip()
                    except NoSuchElementException:
                        comment_info["date"] = None

                    # コメント本文の抽出
                    try:
                        text = comment_el.find_element(By.TAG_NAME, "tt").text.strip()
                        comment_info["text"] = text.replace("\n", " ").replace(",", "")
                    except NoSuchElementException:
                        comment_info["text"] = None

                    comments_list.append(comment_info)
            else:
                print("コメント履歴は見つかりませんでした。")  # 「すべて表示する」クリック後も見つからなかった場合

        except Exception as e:
            print(f"コメント履歴の抽出中にエラーが発生しました: {e}")
        detail_data["コメント履歴"] = comments_list


    except TimeoutException:
        print(f"エラー: 詳細ページ ({detail_url}) の読み込みがタイムアウトしました。")
        driver.save_screenshot("detail_page_timeout_screenshot.png")
    except Exception as e:
        print(f"エラー: 詳細ページ ({detail_url}) からのデータ抽出中に問題が発生しました: {e}")
        driver.save_screenshot("detail_page_error_screenshot.png")

    return detail_data


def csv_create(records):
    try:
        file_name = "workflow.csv"

        fieldnames = [
            '申請番号', '申請日', '申請者', '申請名', '申請内容',
            '対応者', '対応内容', '添付資料1', '添付資料2', '添付資料3',
            'コメント履歴'
        ]

        #for record in records:

        #print(records)

        with open(file_name, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # ヘッダー行を書き込む
            writer.writeheader()
            writer.writerows(records)

            # 整形されたデータを書き込む
            #for row in records:
            #    writer.writerows(row)
    except Exception as e:
        print(e)


# メイン処理
if __name__ == "__main__":
    driver = None
    try:
        driver = setup_driver()

        if not login_to_cybozu(driver, USERNAME, PASSWORD):
            print("ログインに失敗しました。プログラムを終了します。")
            driver.quit()
            exit()

        if not navigate_to_workflow_list(driver):
            print("ワークフロー一覧ページへの遷移に失敗しました。プログラムを終了します。")
            driver.quit()
            exit()

        # ページネーションを考慮して全てのワークフローデータを抽出
        workflow_records = extract_all_workflow_data_with_pagination(driver)

        all_detailed_workflow_data = []

        #print(f"\n--- 全てのワークフローデータ ({len(workflow_records)}件) ---")
        #for i, record in enumerate(workflow_records):
        #    print(f"レコード {i + 1}: {record}")
        #    if i >= 4:  # 最初の方の5件だけ表示
        #        print("...")
        #        break
        #print(len(workflow_records))

        for i, record in enumerate(workflow_records):
            detailed_data = extract_detail_data(driver, record['detail_url'])
            all_detailed_workflow_data.append(detailed_data)

        output_data_for_writer = []

        for workflow_detail in all_detailed_workflow_data:
            row_to_write = {}

            for field in ['申請番号', '申請日', '申請者', '申請名', '申請内容', '対応者', '対応内容']:
                row_to_write[field] = workflow_detail.get(field, '')

            for i in range(1,4):
                attachment_files_list = workflow_detail.get(f'添付資料{i}', None)

                combined_attachment_info_parts = []
                if attachment_files_list:
                    for file_info in attachment_files_list:
                        file_name = file_info.get('name', '')
                        file_url = file_info.get('url', '')

                        if file_name and file_url:
                            combined_attachment_info_parts.append(f"{file_name} ({file_url})")
                        elif file_name:
                            combined_attachment_info_parts.append(file_name)
                        elif file_url:  # 名前がないがURLがある場合
                            combined_attachment_info_parts.append(file_url)
                row_to_write[f'添付資料{i}'] = "　".join(combined_attachment_info_parts)

            comments_list = workflow_detail.get('コメント履歴', [])
            combined_comment_parts = []
            for comment_dict in comments_list:
                serial_number = comment_dict.get('number', '')
                creator_name = comment_dict.get('creator_name', '')
                date = comment_dict.get('date', '')
                text = comment_dict.get('text', '')

                formatted_comment = (
                    f"{serial_number}:"
                    f"{creator_name}　"
                    f"{date}　"
                    f"{text}"
                )
                combined_comment_parts.append(formatted_comment)

            row_to_write['コメント履歴'] = "　".join(combined_comment_parts)

            output_data_for_writer.append(row_to_write)

        csv_create(output_data_for_writer)

    except Exception as e:
        print(f"スクリプトの実行中に致命的なエラーが発生しました: {e}")
    finally:
        if driver:
            print("\nブラウザを閉じます。")
            driver.quit()