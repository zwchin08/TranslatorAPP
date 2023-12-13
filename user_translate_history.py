import pymysql
from flask import Flask, render_template, request, redirect, jsonify, session
from flask import Blueprint

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


@history_bp.route("/user_translate_history/<int:index>", methods=["GET", "POST"])
def user_translate_history(index):
    if request.method == "GET":
        if 'user_id' not in session or session['user_id'] is None:
            return render_template(f"login_signup.html")
        return render_template(f"user_translate_history{index}.html")

    if request.method == "POST":
        data = request.get_json()
        user_id = session['user_id']
        input_language = data.get("input_language")
        output_language = data.get("output_language")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        search_keyword = data.get("search_keyword")
        sort_order = data.get("sort_order")
        page = data.get("page", 1)  # 默认为第一页
        favoritesValue = data.get("favoritesValue")

        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            if favoritesValue == "1":
                sql_query = "SELECT id, input_text, output_text, update_time, collect FROM history_list WHERE user_id = %s and collect = %s"
                params = [user_id, favoritesValue]

            elif favoritesValue == "0":
                sql_query = "SELECT id, input_text, output_text, update_time, collect FROM history_list WHERE user_id = %s"
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

            # 分页逻辑
            total_results = len(all_results)
            items_per_page = 10
            total_pages = (total_results + items_per_page - 1) // items_per_page

            start_index = (page - 1) * items_per_page
            end_index = start_index + items_per_page
            paginated_results = all_results[start_index:end_index]

            return jsonify({
                "data_list": paginated_results,
                "total_pages": total_pages,
                "current_page": page,
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        finally:
            cursor.close()
            conn.close()


@history_bp.route("/mark_item_updated/<int:index>", methods=["POST"])
def update_translation_item(index):
    if request.method == "POST":
        data = request.json
        get_id = data.get("id")
        get_fav = data.get("fav")

        if get_id is not None:
            conn = connect_to_database()
            cursor = conn.cursor()

            try:
                update_query = "UPDATE history_list SET collect = %s WHERE id = %s"
                params = [get_fav, get_id]
                cursor.execute(update_query, params)
                conn.commit()

            except Exception as e:
                return jsonify({"error": str(e)}), 500

            finally:
                cursor.close()
                conn.close()

            return jsonify({"success": True})

        else:
            return jsonify({"success": False, "message": "Invalid request"})


@history_bp.route("/delete_item/<int:index>", methods=['POST'])
def delete_translation_list(index):
    nid = request.json.get('id')
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM history_list WHERE id = %s", (nid,))
        conn.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

    return redirect(f'/user_translate_history/{index}')
