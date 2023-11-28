import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
from flask import Blueprint, request, jsonify
import chatgpt_robot

chat_bp = Blueprint('chat_bp', __name__)

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


@chat_bp.route("/user_chatbot_page/<int:index>", methods=["GET", "POST"])
def user_chatbot_page(index):
    if request.method == "GET":
        if index in range(1, 5):
            return render_template(f"user_chatbot_page{index}.html")
        else:
            return "Invalid index"
    if request.method == "POST":
        text = request.form.get("textToTranslate")
        output_language = request.form.get("outputLanguage")
        result = chatgpt_robot.chatbot(text)
        return render_template(f"user_chatbot_page{index}.html", result=result)
