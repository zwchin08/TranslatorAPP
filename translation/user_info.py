from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
import chatgpt_robot
import top_page
from flask import Blueprint, request, jsonify

user_bp = Blueprint('user', __name__)

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


# 返回用户个人信息页
@user_bp.route("/user_info/<int:index>", methods=["GET"])
def user_info(index):
    return render_template(f"user_info{index}.html")


# 获取用户信息的API
@user_bp.route('/api/getUserInfo', methods=['GET'])
def get_user_info():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({'error': '用户未登录'})

    user_id = session['user_id']  # 获取已登录用户的ID
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
    conn.commit()
    user_data = cursor.fetchone()
    print(user_data)
    close_database_connection(conn, cursor)
    return jsonify(user_data)



# 第一次验证是不是当前用户

@user_bp.route('/api/validatePassword', methods=['POST'])
def validate_password():
    try:
        data = request.get_json()
        current_password = data.get('currentPassword')
        print("用户第一次密码验证:",current_password)
        user_id = session.get('user_id')
        # user_id = session['user_id']  # 获取已登录用户的ID
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
        conn.commit()
        user_info = cursor.fetchone()
        stored_password = user_info['password']

        close_database_connection(conn, cursor)
        # 在这里实现密码验证逻辑，将用户输入的密码与数据库中的密码哈希值进行比较
        if bcrypt.checkpw(current_password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '密码验证失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# 更新用户信息的API
@user_bp.route('/api/updateUserInfo', methods=['POST'])
def update_user_info():
    try:
        data = request.get_json()# 从请求中获取JSON数据
        newPassword = data.get('newPassword1')
        newEmail = data.get('newEmail')
        print("新得密码",  newPassword, "新邮箱", newEmail)
        user_id = session.get('user_id')
        # user_id = session['user_id']  # 获取已登录用户的ID
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        hashed_password = bcrypt.hashpw(newPassword.encode('utf-8'), bcrypt.gensalt())  # 使用bcrypt进行密码哈希
        cursor.execute("UPDATE admin SET password = %s,email = %s WHERE id = %s", (hashed_password, newEmail,user_id))
        cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
        conn.commit()
        user_data = cursor.fetchone()
        print(user_data)

        user_id = session['user_id']  # 获取已登录用户的ID
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
        conn.commit()
        user_data = cursor.fetchone()
        print(user_data)
        close_database_connection(conn, cursor)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
