from getpass import getpass
from flask import session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
import chatgpt_robot
import top_page
import user

# 配置数据库连接信息
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
1.本函数用于创建新用户
2.创建成功后会自动跳转到登陆页面
3.给用户发送Email通知
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
        return []  # 注册成功时返回空的错误消息列表

    return error_messages  # 返回错误消息列表


"""
1.该方法用于用户登录
2.登陆后会跳转到该用户的登录画面
"""


def login_user(index):
    login_username = request.form.get("username")
    login_password = request.form.get("pwd")

    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin ")
    user_data = cursor.fetchall()
    print(user_data)
    user_info = None
    for user in user_data:
        if user['username'] == login_username:
            user_info = user
            break
    if user_info:
        # 找到用户信息，验证密码
        stored_password = user_info['password']
        if bcrypt.checkpw(login_password.encode('utf-8'), stored_password.encode('utf-8')):
            # 密码验证成功，允许用户登录
            print("loginしました。")
            return redirect(f"/user_translation_page/{index}")
        else:
            # 密码验证失败，拒绝登录
            print("login失败しました。")
            return redirect(f"/login/{index}")
    else:
        # 用户名不存在，拒绝登录
        print("ユーザ名が不存在")
        return redirect(f"/login{index}")

    close_database_connection(conn, cursor)


'''
1.当用户忘记密码时会通过邮箱进行重新设定
2.为了安全起见，使用了相关的加密处理
3.流程为:  忘记密码 ——》2.邮箱--》3.重置密码
'''
# 存储密码重置令牌的字典
reset_tokens = {}


def generate_reset_token():
    token_length = 64
    characters = string.ascii_letters + string.digits
    reset_token = ''.join(random.choice(characters) for _ in range(token_length))
    return reset_token


def send_signup_email(index, email):
    signup_link = f"http://127.0.0.1:5000/login/{index}"
    # 创建电子邮件对象
    msg = MIMEMultipart()
    msg['From'] = 'chinseii@126.com'
    msg['To'] = email
    msg['Subject'] = 'Password Reset'
    body = f'おめでとうございます、翻訳アプリのアカウントが作成されました。ログインするためにリンクをクリックしてください。: {signup_link}'
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
    body = f'Click the following link to reset your password: {reset_link}'
    msg.attach(MIMEText(body, 'plain'))
    try:
        # 连接到邮件服务器并发送电子邮件（使用SSL加密）
        server = smtplib.SMTP_SSL('smtp.126.com', 465)
        server.login('chinseii@126.com', 'XLZQTRYNSEZDBQTW')
        text = msg.as_string()
        server.sendmail('chinseii@126.com', email, text)
        server.quit()
        return "邮件成功发送"
    except smtplib.SMTPException as e:
        return f"邮件发送失败: {str(e)}"


def password_forgot(index):
    if request.method == "POST":
        email = request.form.get("email")
        # 检查用户是否存在，如果存在，生成重置令牌并发送邮件
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        user_data = cursor.fetchone()

        if user_data:
            user_id = user_data['id']
            reset_token = generate_reset_token()
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=15)  # 令牌的有效期为1小时
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
    session["reset_token"] = token  # 存储 token 到会话中
    # print("GET请求中的token值：", token)
    return render_template(f"password_reset{index}.html")


def password_reset_post(index):
    token = session.get("reset_token")  # 从会话中获取 token
    # print("POST请求中的token值：", token)
    new_password = request.form.get("new_password1")
    # print("POST请求中的new_password值：", new_password)
    # 查询数据库以验证令牌的有效性和过期性
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM password_reset_tokens WHERE token = %s AND expires_at > NOW()", (token,))
    token_data = cursor.fetchone()
    # print("从数据库中获取的token_data值：", token_data)

    if token_data:
        # 令牌有效，允许用户更新密码
        user_id = token_data['user_id']
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())  # 使用bcrypt进行密码哈希
        cursor.execute("UPDATE admin SET password = %s WHERE id = %s", (hashed_password, user_id))
        cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
        conn.commit()
        close_database_connection(conn, cursor)
        return "新しいパスワードが正常にリセットされました。"
    else:
        close_database_connection(conn, cursor)
        return "無効または期限切れのトークンです。"
