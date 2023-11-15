from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "hsp",
    "charset": "utf8",
    "db": "translationapp",
}


def connect_to_database():
    return pymysql.connect(**DB_CONFIG)


def close_database_connection(conn, cursor):
    cursor.close()
    conn.close()


"""
1.この関数は新しいユーザーを作成するために使用されます。
2.作成が成功すると、自動的にログインページにリダイレクトされます。
3.ユーザーに対してEメール通知が送信されます。
"""


def log_up(index):
    error_messages = []

    username = request.form.get("username")
    password = request.form.get("pwd")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    email = request.form.get("email")

    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    # language=sql
    cursor.execute("select * from admin ")
    user_data = cursor.fetchall()
    for user in user_data:
        if user['username'] == username:
            error_messages.append("このユーザーネームは既に他のユーザーによって使用されています。別のユーザーネームを選んでください.")
        if user['email'] == email:
            error_messages.append("このメールアドレスは既に他のユーザーによって使用されています。別のメールアドレスを入力してください.")

    if not error_messages:
        send_signup_email(index, email)
        sql = "INSERT INTO admin (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, [username, email, hashed_password])
        conn.commit()
        close_database_connection(conn, cursor)
        return []  #登録成功時にはエラーメッセージのリストを空で返します

    return error_messages  # 返回错误消息列表


"""

1.このメソッドはユーザーのログインに使用されます。
2.ログイン後、そのユーザーのログイン画面にリダイレクトされます。

"""


def login_user(index):
    login_username = request.form.get("username")
    login_password = request.form.get("pwd")

    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin ")
    # cursor.execute("SELECT * FROM user_list ")
    user_data = cursor.fetchall()
    print(user_data)
    user_info = None
    for user in user_data:
        if user['username'] == login_username:
            user_info = user
            break
    if user_info:
        stored_password = user_info['password']
        if bcrypt.checkpw(login_password.encode('utf-8'), stored_password.encode('utf-8')):
            # ユーザー情報をセッションに保存します
            session['user_id'] = user_info['id']
            print("loginしました。")
            return redirect(f"/user_translation_page/{index}")
        else:
            print("login失败しました。")
            return redirect(f"/login/{index}")
    else:
        print("ユーザ名が不存在")
        return redirect(f"/login/{index}")

    close_database_connection(conn, cursor)


'''
1.ユーザーがパスワードを忘れた場合、メールを使用して再設定します。
2.セキュリティのため、関連する暗号化処理が使用されています。
3.手順: パスワードを忘れる ——》2.メール ——》3.パスワードのリセット
'''
# パスワードリセットトークンを格納する辞書
reset_tokens = {}

def generate_reset_token():
    token_length = 64
    characters = string.ascii_letters + string.digits
    reset_token = ''.join(random.choice(characters) for _ in range(token_length))
    return reset_token


def send_signup_email(index, email):
    signup_link = f"http://127.0.0.1:5000/login/{index}"
    #電子メールオブジェクトの作成
    msg = MIMEMultipart()
    msg['From'] = 'chinseii@126.com'
    msg['To'] = email
    msg['Subject'] = 'Password Reset'
    # body = f'おめでとうございます、翻訳アプリのアカウントが作成されました。ログインするためにリンクをクリックしてください。: {signup_link}'
    signup_link = f"http://127.0.0.1:5000/login/{index}"
    body = f'''
    C-Teamへのユーザー登録をお申し込みいただきありがとうございます。
    登録手続きを完了するには、こちらのURLにアクセスしてください:

    {signup_link}

    なお、このURLは送信より12時間有効です。
    有効期限切れの場合は最初から手続きをやり直してください。

    ※このメールに心当たりのない方は破棄してください。
    ※このメールは送信専用です。ご返信いただいても対応できません。

    ------------------------------
    C-Team(C-チーム)
    https://chenzhengwei-website2.netlify.app/
    '''

    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP_SSL('smtp.126.com', 465)
        server.login('chinseii@126.com', 'XLZQTRYNSEZDBQTW')
        text = msg.as_string()
        server.sendmail('chinseii@126.com', email, text)
        server.quit()
        return "邮件成功发送"
    except smtplib.SMTPException as e:
        return f"邮件发送失败: {str(e)}"


def send_reset_email(index, email, reset_token):
    reset_link = f"http://127.0.0.1:5000/password_reset/{index}?token={reset_token}"
    # 创建电子邮件对象
    msg = MIMEMultipart()
    msg['From'] = 'chinseii@126.com'
    msg['To'] = email
    msg['Subject'] = 'Password Reset'
    # 邮件正文
    body = f'''
    以下のリンクをクリックしてパスワードをリセットしてください： 
    {reset_link}
    なお、このURLは送信より12時間有効です。
    有効期限切れの場合は最初から手続きをやり直してください。

    ※このメールに心当たりのない方は破棄してください。
    ※このメールは送信専用です。ご返信いただいても対応できません。

    ------------------------------
    C-Team(C-チーム)
    https://chenzhengwei-website2.netlify.app/
    '''
    msg.attach(MIMEText(body, 'plain'))
    try:
        # メールサーバーに接続して電子メールを送信する（SSL暗号化を使用)
        server = smtplib.SMTP_SSL('smtp.126.com', 465)
        server.login('chinseii@126.com', 'XLZQTRYNSEZDBQTW')
        text = msg.as_string()
        server.sendmail('chinseii@126.com', email, text)
        server.quit()
        return "メールの送信が成功しました"
    except smtplib.SMTPException as e:
        return f"メールの送信に失敗しました: {str(e)}"


def password_forgot(index):
    if request.method == "POST":
        email = request.form.get("email")
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        user_data = cursor.fetchone()

        if user_data:
            user_id = user_data['id']
            reset_token = generate_reset_token()
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=1)  # トークンの有効期間は1時間です
            cursor.execute("INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
                           (user_id, reset_token, expires_at))
            conn.commit()
            close_database_connection(conn, cursor)

            result = send_reset_email(index, email, reset_token)
            if "Email sending failed" in result:
                return result
            else:
                return "パスワードのリセット手順がメールで送信されました。"
        else:
            close_database_connection(conn, cursor)
            return "User not found"

    return render_template(f"password_forgot{index}.html")


def password_reset_get(index):
    token = request.args.get("token")
    # トークンをセッションに保存する
    session["reset_token"] = token
    # print("GET请求中的token值：", token)
    return render_template(f"password_reset{index}.html")


def password_reset_post(index):
    token = session.get("reset_token")
    # print("POST请求中的token值：", token)
    new_password = request.form.get("new_password1")
    # print("POST请求中的new_password值：", new_password)
    # データベースを検索してトークンの有効性と期限切れを検証する
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM password_reset_tokens WHERE token = %s AND expires_at > NOW()", (token,))
    token_data = cursor.fetchone()
    # print("从数据库中获取的token_data值：", token_data)

    if token_data:
        # トークンが有効で、ユーザーはパスワードを更新することが許可されています
        user_id = token_data['user_id']
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())  #パスワードのハッシュ化にbcryptを使用する
        cursor.execute("UPDATE admin SET password = %s WHERE id = %s", (hashed_password, user_id))
        cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
        conn.commit()
        close_database_connection(conn, cursor)
        return "新しいパスワードが正常にリセットされました。"
    else:
        close_database_connection(conn, cursor)
        return "無効または期限切れのトークンです。"
