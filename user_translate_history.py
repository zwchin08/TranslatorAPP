import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
from flask import Blueprint, request, jsonify

history_bp = Blueprint('history', __name__)

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


@history_bp.route("/user_translate_history/<int:index>", methods=["GET", "POST"])
def user_translate_history(index):
    if request.method == "GET":
        return render_template(f"user_translate_history{index}.html")
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
        page = data.get("page", 1)  # 默认为第一页
        favoritesValue = data.get("favoritesValue")
        print("favoritesValue", favoritesValue)
        print(type(favoritesValue))

        conn = connect_to_database()
        cursor = conn.cursor()

        if favoritesValue == "1":
            sql_query = "SELECT id,input_text,output_text,update_time,collect FROM history_list WHERE user_id = %s and collect = %s"
            params = [user_id, favoritesValue]

        elif favoritesValue == "0":
            print("favoritesValue 0", favoritesValue)
            sql_query = "SELECT id,input_text,output_text,update_time,collect FROM history_list WHERE user_id = %s"
            params = [user_id]

        if input_language:
            sql_query += " AND input_language = %s"
            params.append(input_language)

        if output_language:
            sql_query += " AND output_language = %s"
            params.append(output_language)

        if start_date and end_date:
            sql_query += " AND create_time BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        if search_keyword:
            sql_query += " AND input_text LIKE %s"
            params.append(f"%{search_keyword}%")

        if sort_order == 0:
            sql_query += " ORDER BY update_time ASC"
        else:
            sql_query += " ORDER BY update_time DESC"

        cursor.execute(sql_query, params)

        all_results = cursor.fetchall()
        print(all_results)

        # ページ情報の計算
        total_results = len(all_results)
        items_per_page = 10
        total_pages = (total_results + items_per_page - 1) // items_per_page

        if page is None or items_per_page is None:
            # パラメータが不足している場合、エラーレスポンスを返す処理を行います
            return jsonify({'error': 'Missing page or items_per_page'}), 400

        # ページ情報に基づいて結果を切り取る
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        paginated_results = all_results[start_index:end_index]

        close_database_connection(conn, cursor)

        return jsonify({
            "data_list": paginated_results,
            "total_pages": total_pages,
            "current_page": page,

        })


@history_bp.route("/mark_item_updated/<int:index>", methods=["POST"])
def update_translation_item(index):
    if request.method == "POST":
        data = request.json
        get_id = data.get("id")
        get_fav = data.get("fav")
        print(get_id)
        print("fav", get_fav)

        if get_id is not None:
            conn = connect_to_database()
            cursor = conn.cursor()

            if get_fav == 0:
                update_query = "UPDATE history_list SET collect = 0 WHERE id = %s"
                params = [get_id]
                cursor.execute(update_query, params)
                conn.commit()
            if get_fav == 1:
                update_query = "UPDATE history_list SET collect = 1 WHERE id = %s"
                params = [get_id]
                cursor.execute(update_query, params)
                conn.commit()

            cursor.close()
            conn.close()

            return render_template(f"user_translate_history{index}.html")
        else:
            return jsonify({"success": False, "message": "Invalid request"})


@history_bp.route("/delete_item/<int:index>", methods=['POST'])
def delete_translation_list(index):
    nid = request.json.get('id')
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM  history_list WHERE id = %s", (nid,))
    conn.commit()
    close_database_connection(conn, cursor)
    return redirect(f'/user_translate_history/<int:{index}>')
