from django.shortcuts import render
from django.http import JsonResponse
import openai

openai.api_key = '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'

def chat(MSGS, MaxToken=50):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=MSGS,
        max_tokens=MaxToken
    )
    return response.choices[0].message['content']


def submit():
    messages = ["Hello", "Hi", "who won world cup 2018?"]

    MSGS = [{"role": "user" if i % 2 == 0 else "assistant", "content": message} for i, message in enumerate(messages)]

    MSGS.append({"role": "system", "content": "You are an assistant"})

    response = chat(MSGS)
    print(response)

submit()