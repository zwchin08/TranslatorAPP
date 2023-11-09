import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def chatgpt_robot(theInputLanguage, theOutputLanguage, text):
    inputLanguage = theInputLanguage
    outputLanguage = theOutputLanguage
    systemContent = "You will be given with a sentence in " + inputLanguage + ", and your task is to translate it into " + outputLanguage + ". Only need the translation, no need to add unrelated sentences."
    userContent = text
    print(systemContent)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",

        messages=[
            {"role": "system", "content": systemContent},
            {"role": "user", "content": userContent}
        ],
        temperature=0.1,
        top_p=0.1
    )

    print(completion.choices[0].message.content)

    result = completion.choices[0].message.content

    return result


def chatbot(text):

    systemContent = "You will be given a question and your task is to answer it."
    userContent = text
    print(systemContent)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",

        messages=[
            {"role": "system", "content": systemContent},
            {"role": "user", "content": userContent}
        ],
        temperature=0.1,
        top_p=0.1
    )

    result = completion.choices[0].message.content

    return result


# print(openai.api_key)
