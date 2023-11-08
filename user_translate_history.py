from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
import chatgpt_robot
import top_page
from flask import Blueprint, request, jsonify

history_bp = Blueprint('history', __name__)

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


# # 返回用户个人信息页
# @history_bp.route("/your_backend_endpoint", methods=["GET", "POST"])
# def your_backend_endpoint():
#     if request.method == "GET":
#         return render_template("user_translate_history888.html")
#     if request.method == "POST":
#         # 获取前端发送的数据
#         data = request.get_json()
#         user_id = session['user_id']
#         input_language = data.get("input_language")
#         output_language = data.get("output_language")
#         start_date = data.get("start_date")
#         end_date = data.get("end_date")
#         search_keyword = data.get("search_keyword")
#         sort_order = data.get("sort_order")
#
#         print(data)
#         print(user_id)
#         print(input_language)
#         print(output_language)
#
#         # 在这里执行需要的操作，比如查询数据库
#         # 这里使用示例数据来构建响应
#
#
#         # 返回结果给前端
#         return jsonify(data)


@history_bp.route("/your_backend_endpoint", methods=["GET", "POST"])
def your_backend_endpoint():
    if request.method == "GET":
        return render_template("user_translate_history888.html")
    if request.method == "POST":
        data = request.get_json()
        print(data)
        user_id = session['user_id']
        input_language = data.get("input_language")
        output_language = data.get("output_language")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        search_keyword = data.get("search_keyword")
        sort_order = data.get("sort_order")

        # 连接到数据库
        conn = connect_to_database()
        cursor = conn.cursor()

        # 构建SQL查询
        # 构建查询SQL语句
        query = (
            "SELECT * FROM history_list "
            "WHERE user_id = %s AND input_language = %s AND output_language = %s "
            "AND create_time BETWEEN %s AND %s AND input_text LIKE %s "
            "ORDER BY update_time DESC"
        )

        # 执行查询
        cursor.execute(query, (8, input_language, output_language, start_date, end_date, f"%{search_keyword}%"))

        # 获取结果
        results = cursor.fetchall()
        print(results)

        # 关闭数据库连接
        cursor.close()
        conn.close()

        return jsonify(results)
