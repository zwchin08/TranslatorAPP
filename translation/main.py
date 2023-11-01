from collections import OrderedDict
import pymysql,bcrypt
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

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


@app.route("/top")
def top():
    return render_template("top.html")

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


@app.route("/passwordForgot", methods=["GET", "POST"])
def passwordForgot():
    if request.method == "GET":
        return render_template("passwordForgot.html")

@app.route("/index/<int:index>", methods=["GET", "POST"])
def hello_world(index):
    if index in range(1, 5):
        return render_template(f"index{index}.html")
    else:
        return "Invalid index"


@app.route("/test/<int:index>", methods=["POST"])
def test(index):
    if request.method == "POST":
        text = request.form.get("textToTranslate")
        insert_translation(text)
        return render_template(f"index{index}.html", text2=text)



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
