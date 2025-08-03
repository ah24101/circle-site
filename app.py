from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import requests
import os
from datetime import datetime, timedelta

def format_timestamp(iso_str):
    try:
        iso_str = iso_str.replace("Z", "")
        try:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")

        dt_jst = dt + timedelta(hours=9)
        return dt_jst.strftime("%Y/%m/%d %H:%M:%S")
    except Exception as e:
        print(f"[format_timestamp error] {e} 入力: {iso_str}")
        return iso_str






app = Flask(__name__)
app.secret_key = 'a8f7e5d4c3b2a1' 

import requests

# 自動読み込みする
def load_users_from_sheet():
    SHEET_URL = "https://script.google.com/macros/s/AKfycby3OJtxlVgnyOYNyJEUq9i1nH7Wbe_QC04ffgzs_t3mZ6JP_JobN1hJglwyKKpSr03a/exec"  # デプロイしたURL

    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        data = response.json()

        users = {}
        for row in data:
            email = row.get("学籍番号", "") + "@shibaura-it.ac.jp"

            password = row.get("パスワード") or row.get("password") or row.get("Password")
            if email and password:
                users[email] = password
        return users

    except Exception as e:
        print(f"ユーザーデータ取得失敗: {e}")
        return {}

# グローバルに読み込む（Flask起動時）
users = load_users_from_sheet()


# robots.txt を提供するためのルート
@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print(f"ログイン試行: {email} / {password}")
        print(f"登録ユーザー一覧: {users}")  # ←追加して確認

        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for('index'))
        else:
            return "ログインに失敗しました。メールアドレスかパスワードが違います。"
    return render_template('login.html')



@app.route('/mypage')
def mypage():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']
    student_id = email.split('@')[0] # @の前を抽出

    AS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxMTrGHaEn4yzF1ZR3p207ce1kkvBnLzWvHx09w6Y-N3tyXCtODuwZb4cHMmXJta79zrw/exec" 

    event_history = [] 
    error_message = None 

    try:
        response = requests.get(AS_WEB_APP_URL)
        response.raise_for_status() 

        all_data = response.json()

        for record in all_data:
            if record.get('学籍番号') == student_id:
        # JSTに整形したタイムスタンプに書き換え
                record['タイムスタンプ'] = format_timestamp(record['タイムスタンプ'])
                event_history.append(record)


    except requests.exceptions.RequestException as e:
        error_message = f"データの取得に失敗しました。ネットワーク接続を確認してください。エラー: {e}"
        print(f"Error fetching data from Google Apps Script: {e}")
    except ValueError as e:
        error_message = f"受信したデータが不正です。スプレッドシートやApps Scriptのコードを確認してください。エラー: {e}"
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        error_message = f"予期せぬエラーが発生しました: {e}"
        print(f"An unexpected error occurred: {e}")

    return render_template('mypage.html',
                           student_id=student_id,
                           event_history=event_history,
                           error=error_message)
    

def format_date_only(iso_str):
    try:
        iso_str = iso_str.replace("Z", "")
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f")
        return dt.strftime("%Y/%m/%d")
    except:
        return iso_str

def format_date_only(iso_str):
    try:
        iso_str = iso_str.replace("Z", "")
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f")
        return dt.strftime("%Y/%m/%d")
    except:
        return iso_str

@app.route("/event_detail/<event_name>")
def event_detail(event_name):
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]
    student_id = email.split("@")[0]

    GAS_URL = "https://script.google.com/macros/s/AKfycbyJejZf-sbMA1ta_VYeACVvmXGlN3PvwoXoprmNIfbXGmKj6W9ap-mdbj79LPJQJ864/exec"

    try:
        res = requests.get(GAS_URL)
        res.raise_for_status()
        all_data = res.json()

        # 学籍番号とイベント名で絞り込み＋日付整形
        filtered = []
        for row in all_data:
            if row.get("学籍番号") == student_id and row.get("元シート名") == event_name:
                row["参加日時"] = format_date_only(row.get("参加日時", ""))
                filtered.append(row)

        return render_template("event_detail.html", event_name=event_name, records=filtered)

    except Exception as e:
        return f"エラー: {e}"



@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


from datetime import datetime, timedelta

def format_timestamp(iso_str):
    try:
        iso_str = iso_str.replace("Z", "")
        try:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")

        dt_jst = dt + timedelta(hours=9)
        return dt_jst.strftime("%Y/%m/%d")  # 日付だけ表示
    except Exception as e:
        print(f"format_timestamp error: {e} 入力: {iso_str}")
        return iso_str


@app.route('/survey_history')
def survey_history():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    student_id = email.split('@')[0]

    AS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyJejZf-sbMA1ta_VYeACVvmXGlN3PvwoXoprmNIfbXGmKj6W9ap-mdbj79LPJQJ864/exec"

    survey_records = []
    error_message = None

    try:
        response = requests.get(AS_WEB_APP_URL)
        response.raise_for_status()
        all_data = response.json()

        for record in all_data:
            if record.get('学籍番号') == student_id:
                # 参加日時をフォーマット
                if '参加日時' in record:
                    record['参加日時'] = format_timestamp(record['参加日時'])
                survey_records.append(record)

    except Exception as e:
        error_message = f"データの取得に失敗しました: {e}"
        print(error_message)

    return render_template('survey_history.html',
                           student_id=student_id,
                           survey_records=survey_records,
                           error=error_message)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run(debug=True, host='0.0.0.0', port=port)
