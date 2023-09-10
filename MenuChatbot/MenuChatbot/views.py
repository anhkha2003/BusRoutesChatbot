from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from PyPDF2 import PdfReader
from docx import Document
import openai
import os
import glob


openai.api_key = settings.API_KEY

prompt = "You are an employee of the restaurant/coffee. Once provided with the menu and restaurant descriptions, you work like an employee of the restaurant, answering users' questions and making tailored dish suggestions based on users' preferences, do not mention anything about the menu and you have to answer like you know everything about restaurants. Do not give so specific and long answers, make the customer comfortable and attract them with dishes and restaurants. Always show respect to customers and don't need to welcome customer every time. Here is the menu:\n"

def home_view(request):
    context = {
        "bot_message": "Hello! How can I assist you today?",
        "user_avatar_url": settings.USER_AVATAR_URL,
        "bot_avatar_url": settings.BOT_AVATAR_URL,
    }
    return render(request, 'home.html', context)


def chat(MSGS, MaxToken=100):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=MSGS,
        max_tokens=MaxToken
    )
    return response.choices[0].message['content']


def read_file(path):
    filename, file_extension = os.path.splitext(path)
    content = ""

    if file_extension == '.txt':
        with open(path, 'r') as file:
            content = file.read()

    elif file_extension == '.pdf':
        pdf = PdfReader(path)
        for page in range(len(pdf.pages)):
            content += pdf.pages[page].extract_text()

    elif file_extension == '.docx':
        doc = Document(path)
        for para in doc.paragraphs:
            content += para.text

    return content


def submit_view(request):
    messages = request.POST.getlist("messages[]")

    MSGS = [{"role": "user" if i % 2 == 0 else "assistant", "content": message} for i, message in enumerate(messages)]
    
    path_file = glob.glob(os.path.join('data', '*'))
    if not path_file:
        return JsonResponse({'error': 'There is no menu'}, status=400)

    menu = prompt + read_file(path_file[0])

    MSGS.append(
        {"role": "system", 
        "content": menu,
    })

    response = chat(MSGS)
    data = {"message": response}

    return JsonResponse(data)


def delete_all_files_in_folder(folder_path):
    files = glob.glob(os.path.join(folder_path, '*'))
    for file in files:
        os.remove(file)


def upload_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        path = 'data/file.' + uploaded_file.name.split('.')[-1]
        delete_all_files_in_folder('data')
        path = default_storage.save(path, uploaded_file)
        return JsonResponse({})

    return JsonResponse({'error': 'Invalid request'}, status=400)
