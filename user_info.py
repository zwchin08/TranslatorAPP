import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
from flask import Blueprint, request, jsonify

user_bp = Blueprint('user', __name__)

app = Flask(__name__)

app.secret_key = 'my_secret_key_123'

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


# ユーザーの個人情報ページに戻る
@user_bp.route("/user_info/<int:index>", methods=["GET"])
def user_info(index):
    return render_template(f"user_info{index}.html")

@user_bp.route("/logout/<int:index>", methods=["GET"])
def logout(index):
    session['user_id'] = None
    return render_template(f"top_page{index}.html")



@user_bp.route('/api/getUserInfo', methods=['GET'])
def get_user_info():
    # ユーザーがログインしているかどうかを確認します
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in.'})

    # ログインしているユーザーのIDを取得
    user_id = session['user_id']
    conn = connect_to_database()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
    conn.commit()
    user_data = cursor.fetchone()
    print(user_data)
    close_database_connection(conn, cursor)
    return jsonify(user_data)



# 最初の検証は現在のユーザーかどうかです

@user_bp.route('/api/validatePassword', methods=['POST'])
def validate_password():
    try:
        data = request.get_json()
        current_password = data.get('currentPassword')
        print("ユーザー初回パスワード検証:",current_password)
        user_id = session.get('user_id')
        # user_id = session['user_id']  # 获取已登录用户的ID
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
        conn.commit()
        user_info = cursor.fetchone()
        stored_password = user_info['password']

        close_database_connection(conn, cursor)
        # ここでパスワード検証ロジックを実装し、ユーザーが入力したパスワードをデータベース内のハッシュ値と比較します
        if bcrypt.checkpw(current_password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'パスワードの検証に失敗しました'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ユーザー情報を更新するAPI
@user_bp.route('/api/updateUserInfo', methods=['POST'])
def update_user_info():
    try:
        data = request.get_json()# リクエストからJSONデータを取得
        newPassword = data.get('newPassword1')
        newEmail = data.get('newEmail')
        print("新しいパスワード",  newPassword, "新しいメール", newEmail)
        user_id = session.get('user_id')
        # user_id = session['user_id']   # ログインしているユーザーのIDを取得
        conn = connect_to_database()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        hashed_password = bcrypt.hashpw(newPassword.encode('utf-8'), bcrypt.gensalt())  # bcryptを使用してパスワードをハッシュ化
        cursor.execute("UPDATE admin SET password = %s,email = %s WHERE id = %s", (hashed_password, newEmail,user_id))
        cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
        conn.commit()
        user_data = cursor.fetchone()
        print(user_data)

        user_id = session['user_id']  # ログインしているユーザーのIDを取得
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
