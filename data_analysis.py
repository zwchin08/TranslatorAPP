import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
from flask import Blueprint, request, jsonify

data_ana = Blueprint('data_anaiysis', __name__)

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


@data_ana.route("/data_analysis", methods=["GET", "POST"])
def data_analysis():
    if request.method == "GET":
        user_id = session['user_id']
        conn = connect_to_database()
        cursor = conn.cursor()
        # language=sql
        cursor.execute("select * from history_list where user_id = %s ", user_id)
        all_results = cursor.fetchall()
        print(all_results)

        close_database_connection(conn, cursor)

        return jsonify({
            "data_list": all_results,
        })
