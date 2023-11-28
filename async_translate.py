import aiohttp
import os
import openai


from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

openai_api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key:", openai_api_key)

async def async_translate_text(inputLanguage, outputLanguage, text):
    openai.api_key = os.getenv("OPENAI_API_KEY")  # 设置 API 密钥
    async with aiohttp.ClientSession() as session:
        systemContent = "You will be given with a sentence in " + inputLanguage + ", and your task is to translate it into " + outputLanguage + ". Only need the translation, no need to add unrelated sentences."
        userContent = text

        response = await session.post("https://api.openai.com/v1/engines/gpt-3.5-turbo/completions", json={
            "inputLanguage": inputLanguage,
            "outputLanguage": outputLanguage,
            "text": text
        })

        response_data = await response.json()
        print("Response Data:", response_data)  # 添加这行来查看响应数据
        # 确保在响应数据中存在 'result' 字段，否则进行适当的错误处理
        if 'result' in response_data:
            return response_data['result']
        else:
            # 处理没有 'result' 字段的情况
            return "Translation not available"
