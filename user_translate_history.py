import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
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


@history_bp.route("/user_translate_history", methods=["GET", "POST"])
def user_translate_history():
    if request.method == "GET":
        return render_template("user_translate_history1.html")
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
        print(favoritesValue)
        # 连接到数据库
        conn = connect_to_database()
        cursor = conn.cursor()

        # 初始化查询条件
        sql_query = "SELECT id,input_text,output_text,update_time FROM history_list WHERE user_id = %s"
        params = [user_id]

        if input_language:
            sql_query += " AND input_language = %s"
            params.append(input_language)

        if  favoritesValue:
            sql_query += " AND collect = %s"
            params.append(favoritesValue)

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

        # 执行查询
        cursor.execute(sql_query, params)

        # 获取所有结果
        all_results = cursor.fetchall()
        print(all_results)

        # 计算分页信息
        total_results = len(all_results)
        items_per_page = 10  # 假设每页显示10条记录
        total_pages = (total_results + items_per_page - 1) // items_per_page

        if page is None or items_per_page is None:
            # 处理缺少参数的情况，可以返回错误响应
            return jsonify({'error': 'Missing page or items_per_page'}), 400

        # 根据分页信息截取结果
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        paginated_results = all_results[start_index:end_index]

        # 关闭数据库连接
        close_database_connection(conn, cursor)

        #返回包含分页信息的 JSON 数据
        return jsonify({
            "data_list": paginated_results,
            "total_pages": total_pages,
            "current_page": page
        })





# 在后端路由中处理更新请求
@history_bp.route("/mark_item_updated", methods=["POST"])
def update_translation_item():
    if request.method == "POST":
        # 获取前端发送的数据
        data = request.json
        get_id = data.get("id")
        print(get_id)

        if get_id is not None:
            # 更新数据库中对应行的 collect 字段为1
            conn = connect_to_database()
            cursor = conn.cursor()

            # 假设数据库表为 translation_items，你需要替换成实际的表名
            update_query = "UPDATE history_list SET collect = 1 WHERE id = %s"
            params = [get_id]

            cursor.execute(update_query, params)
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({"success": True, "message": "Item updated successfully"})
        else:
            return jsonify({"success": False, "message": "Invalid request"})

