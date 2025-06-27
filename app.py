from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import requests
import os

app = Flask(__name__)
app.secret_key = 'a8f7e5d4c3b2a1' 

# 仮のユーザー情報：ここでログイン許可する人を指定
users = {
    "ah24101@shibaura-it.ac.jp": "123456"
}

# robots.txt を提供するためのルート
@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
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


@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run(debug=True, host='0.0.0.0', port=port)