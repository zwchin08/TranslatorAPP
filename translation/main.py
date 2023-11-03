from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
import chatgpt_robot
import top_page
import user

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


'''
ホームページにアクセス
'''


@app.route("/top/<int:index>")
def top(index):
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
            # 渲染注册页面并传递错误消息
        return render_template(f"signup{index}.html", error_messages=error_messages)


@app.route("/login/<int:index>", methods=["GET", "POST"])
def login(index):
    if request.method == "GET":
        return render_template(f"login{index}.html")
    return user.login_user(index)


'''
1.忘记密码 ——》2.邮箱--》3.重置密码
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


def insert_translation(text, result):
    conn = connect_to_database()
    cursor = conn.cursor()
    insert_query = 'INSERT INTO tb_01 (input, output) VALUES (%s, %s)'
    cursor.execute(insert_query, (text, result))
    conn.commit()
    close_database_connection(conn, cursor)


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
        insert_translation(text, result)
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
