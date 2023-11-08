# import os
# import openai
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
import pymysql, bcrypt, random, datetime, hashlib, string, smtplib
from flask import Flask, render_template, request, redirect, jsonify, session
import chatgpt_robot
import top_page
from flask import Blueprint, request, jsonify
import main

chat_bp = Blueprint('chat_bp', __name__)

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


# openai.api_key = os.getenv("OPENAI_API_KEY")


# 返回用户个人信息页
@chat_bp.route("/user_chatbot_page/<int:index>", methods=["GET"])
def user_chatbot_page(index):
    if request.method == "GET":
        if index in range(1, 5):
            return render_template(f"user_chatbot_page{index}.html")
        else:
            return "Invalid index"
    if request.method == "POST":
        input_Language = request.form.get("inputLanguage")
        text = request.form.get("textToTranslate")
        output_language = request.form.get("outputLanguage")
        result = chatgpt_robot(input_Language, output_language, text)
        if index != 0:
            main.insert_translation(text, result)
        return render_template(f"user_translation_page{index}.html", result=result)


def chatgpt_robot(theInputLanguage, theOutputLanguage, text):
    inputLanguage = theInputLanguage
    outputLanguage = theOutputLanguage
    # systemContent = "You will be given a question" + inputLanguage + ", and your task is to answer that question " + outputLanguage
    # userContent = text
    # print(systemContent)
    # # completion = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #
    #     messages=[
    #         {"role": "system", "content": systemContent},
    #         {"role": "user", "content": userContent}
    #     ],
    #     temperature=0.1,
    #     top_p=0.1
    # )
    #
    # print(completion.choices[0].message.content)
    #
    # result = completion.choices[0].message.content
    #
    # return result


# openai.api_key = os.getenv("OPENAI_API_KEY")
# print(openai.api_key)
