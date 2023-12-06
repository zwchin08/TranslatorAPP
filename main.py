from collections import OrderedDict
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
import chatgpt_robot
import top_page
import user
from datetime import datetime
import logging
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


# 「user_routes.py」をインポートし、Blueprintに登録
from user_info import user_bp

app.register_blueprint(user_bp)

'''
データ分析
'''
from data_analysis import data_ana
app.register_blueprint(data_ana)


from chatbot import chat_bp

app.register_blueprint(chat_bp)

'''
履歴route作る
'''
from user_translate_history import history_bp

app.register_blueprint(history_bp)

'''
Connect Phone
'''

from flask_socketio import SocketIO

socketio = SocketIO(app)


@app.route('/index')
def index():
    return render_template('phone.html')


@socketio.on('message')
def handle_message(message):
    if 'type' in message and message['type'] == 'computerInput':
        socketio.emit('message', message)


'''
ホームページにアクセス
'''


@app.route("/top/<int:index>")
def top(index):
    session['user_id'] = None
    return top_page.top_page(index)


@app.route("/add_user/<int:index>", methods=["GET", "POST"])
def add_user(index):
    if request.method == "GET":
        if index in range(1, 5):
            return render_template(f"signup{index}.html")
        else:
            return "Invalid index"
    if request.method == "POST":
        error_messages = user.log_up(index)
        if not error_messages:
            return redirect(f"/login/{index}")
        return render_template(f"signup{index}.html", error_messages=error_messages)


@app.route("/login/<int:index>", methods=["GET", "POST"])
def login(index):
    if request.method == "GET":
        return render_template(f"login{index}.html")

    return user.login_user(index)


'''
1.パスワードを忘れる ⟶ 2. メールボックス ⟶ 3. パスワードをリセット
'''


@app.route("/passwordForgot/<int:index>", methods=["POST", "GET"])
def passwordForgot(index):
    if request.method == "GET":
        return render_template(f"password_forgot{index}.html")
    return user.password_forgot(index)


token = ""


@app.route("/password_reset/<int:index>", methods=["POST", "GET"])
def password_reset_get(index):
    print(request.args.get("token"))
    return user.password_reset_get(index)


@app.route("/password_reset_post/<int:index>", methods=["POST"])
def password_reset_post(index):
    return user.password_reset_post(index)


def insert_translation(input_language, input_text, output_language, output_text):
    conn = connect_to_database()
    cursor = conn.cursor()
    user_id = session['user_id']
    create_time = datetime.now()
    update_time = create_time
    collect = 0  # 默认值为0
    language_mapping = {
        'ja-JP': 1,
        'en-US': 2,
        'zh-CN': 3,
        'my-MM': 4,
    }
    input_language_id = language_mapping.get(input_language, 0)  # Default value is 0
    output_language_id = language_mapping.get(output_language, 0)  # Default value is 0
    # print(f"Input Language from Form: {input_language}")
    # print(f"Output Language from Form: {output_language}")
    #
    # print(f"Input Language: {input_language}, Mapped ID: {input_language_id}")
    # print(f"Output Language: {output_language}, Mapped ID: {output_language_id}")

    # データベースに挿入する際に整数値を使用します
    insert_query = 'INSERT INTO history_list(input_language, input_text, output_language, output_text, collect, user_id, create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(insert_query, (
        input_language_id, input_text, output_language_id, output_text, collect, user_id, create_time, update_time))
    conn.commit()
    close_database_connection(conn, cursor)


@app.route("/user_translation_page/<int:index>", methods=["GET", "POST"])
def input_translate_output(index):
    if request.method == "GET":
        if index in range(0, 6):
            return render_template(f"user_translation_page{index}.html")
        else:
            return "Invalid index"
    if request.method == "POST":
        input_language = request.form.get("inputLanguage").strip()
        output_language = request.form.get("outputLanguage").strip()

        # input_Language = request.form.get("inputLanguage")
        text = request.form.get("textToTranslate")
        # output_language = request.form.get("outputLanguage")
        result = chatgpt_robot.chatgpt_robot(input_language, output_language, text)
        if index != 0:
            insert_translation(input_language, text, output_language, result)
        return render_template(f"user_translation_page{index}.html", result=result)


@app.route("/show_translation_list")
def show_translation_list():
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM tb_01")
    data_list = cursor.fetchall()
    close_database_connection(conn, cursor)
    return render_template("translation_list.html", title="翻訳したリスト", data_list=data_list)


@app.errorhandler(500)
def internal_server_error(e):
    logging.error('发生内部服务器错误：%s', e)
    return jsonify(error='内部服务器错误'), 500


# 在某处定义错误处理程序
@app.errorhandler(500)
def internal_server_error(error):
    response = jsonify({'error': 'Internal Server Error'})
    response.status_code = 500
    return response


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


@app.route("/about_website")
def about_website():
    return render_template("about_website.html")


@app.route("/about_website1")
def about_website1():
    return render_template("about_website1.html")


@app.route("/about_website2", methods=["GET", "POST"])
def about_website2():
    if request.method == "GET":
        return render_template("about_website2.html")
    elif request.method == "POST":
        # 从 POST 请求中获取表单数据
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        print(name, message)
        # 连接数据库并执行插入操作
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # language=sql
        cursor.execute("INSERT INTO inquiries (name, email, message) VALUES (%s, %s, %s)",
                       (name, email, message))
        conn.commit()
        close_database_connection(conn, cursor)
        return "お問い合わせが送信されました。ありがとうございます！"


@app.route("/about_team")
def about_team():
    return render_template("about_team.html")


@app.route("/about_code")
def about_code():
    return render_template("about_code1.html")

@app.route("/about_future")
def about_future():
    return render_template("about_future.html")


@app.route("/about_development")
def about_development():
    return render_template("about_development.html")


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


# if __name__ == '__main__':
#     app.run()
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
