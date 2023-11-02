from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
import chatgpt_robot
import top_page

app = Flask(__name__)

app.secret_key = 'my_secret_key_123'

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


def insert_translation(text):
    conn = connect_to_database()
    cursor = conn.cursor()
    insert_query = 'INSERT INTO tb_01 (input, output) VALUES (%s, %s)'
    cursor.execute(insert_query, (text, text))
    conn.commit()
    close_database_connection(conn, cursor)


@app.route("/top/<int:index>")
def top(index):
    return top_page.top_page(index)


# 使用add_user.html可以添加，但是使用login.html添加不了
@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "GET":
        return render_template("signup.html")
    username = request.form.get("username")
    password = request.form.get("pwd")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    email = request.form.get("email")

    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "insert into admin(username, email, password) values (%s, %s, %s)"
    cursor.execute(sql, [username, email, hashed_password])
    conn.commit()
    close_database_connection(conn, cursor)
    return redirect("/login_user")


@app.route("/login_user", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("login02.html")

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
            return redirect("/index/2")
        else:
            # 密码验证失败，拒绝登录
            print("login失败しました。")
            return redirect("/login_user")
    else:
        # 用户名不存在，拒绝登录
        print("ユーザ名が正しくない")
        return redirect("/login_user")

    close_database_connection(conn, cursor)


'''
1.忘记密码 ——》2.邮箱--》3.重置密码
'''

# 存储密码重置令牌的字典
reset_tokens = {}


def generate_reset_token():
    token_length = 64
    characters = string.ascii_letters + string.digits
    reset_token = ''.join(random.choice(characters) for _ in range(token_length))
    return reset_token


def send_reset_email(email, reset_token):
    reset_link = f"http://127.0.0.1:5000/password_reset?token={reset_token}"
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


@app.route("/passwordForgot", methods=["POST", "GET"])
def passwordForgot():
    if request.method == "GET":
        return render_template("passwordForgot.html")

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

            result = send_reset_email(email, reset_token)
            if "Email sending failed" in result:
                return result
            else:
                return "パスワードのリセット手順がメールで送信されました。"
        else:
            close_database_connection(conn, cursor)
            return "User not found"

    return render_template("passwordForgot.html")


token = ""


@app.route("/password_reset", methods=["POST", "GET"])
def password_reset_get():
    token = request.args.get("token")
    session["reset_token"] = token  # 存储 token 到会话中
    print("GET请求中的token值：", token)
    return render_template("password_reset.html")


@app.route("/password_reset_post", methods=["POST"])
def password_reset_post():
    token = session.get("reset_token")  # 从会话中获取 token
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


@app.route("/index/<int:index>", methods=["GET", "POST"])
def input_translate_output(index):
    if request.method == "GET":
        if index in range(1, 5):
            return render_template(f"index{index}.html")
        else:
            return "Invalid index"
    if request.method == "POST":
        input_Language = request.form.get("inputLanguage")
        text = request.form.get("textToTranslate")
        output_language = request.form.get("outputLanguage")
        result = chatgpt_robot.chatgpt_robot(input_Language, output_language, text)
        insert_translation(text)
        return render_template(f"index{index}.html", result=result)


@app.route("/show_translation_list")
def show_translation_list():
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM tb_01")
    data_list = cursor.fetchall()
    close_database_connection(conn, cursor)
    return render_template("translation_list.html", title="翻訳したリスト", data_list=data_list)


@app.route("/delete_translation_list", methods=['POST'])
def delete_translation_list():
    nid = request.form.get('nid')
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tb_01 WHERE id = %s", (nid,))
    conn.commit()
    close_database_connection(conn, cursor)
    return redirect('/show_translation_list')


# 普通のユーザ検索

@app.route("/show_user")
def show_user():
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select * from admin")
    data_list = cursor.fetchall()
    print(data_list)
    close_database_connection(conn, cursor)
    return render_template("show_user.html", title="用户列表", data_list=data_list)


# # super rooter
# @app.route("/user_list")
# def user_list():
#     conn = connect_to_database()
#     cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
#     cursor.execute("select * from user_list")
#     data_list = cursor.fetchall()
#     print(data_list)
#     close_database_connection(conn, cursor)
#     return render_template("user_list.html",  data_list=data_list)

def format_data(data):
    formatted_data = []
    for item in data:
        formatted_item = OrderedDict()
        formatted_item["id"] = item["id"]
        formatted_item["name"] = item["username"]
        formatted_item["image"] = item["image"]
        formatted_item["email"] = item["email"]
        formatted_item["create_time"] = item["create_time"].strftime('%Y-%m-%d')
        formatted_item["update_time"] = item["update_time"].strftime('%Y-%m-%d %H:%M:%S')
        formatted_data.append(formatted_item)
    return formatted_data


@app.route("/getdatabase")
def user_list():
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select * from user_list")
    data_list = cursor.fetchall()
    formatted_data = format_data(data_list)
    print(type(formatted_data))
    close_database_connection(conn, cursor)
    return jsonify(formatted_data)


@app.route("/show_user_list")
def show_user_list():
    return render_template("show_user_list.html")


@app.route("/yemian")
def yemian():
    return render_template("depart_add.html")


if __name__ == '__main__':
    app.run()
