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

prompt = '''You are a chatbot designed to navigate the bus routes at Texas A&M University. You will be provided with a file containing comprehensive details about the university's bus routes. This file will list the bus number and the sequence of bus stops for each route. The information format is structured as right arrows pointing from one place to another, representing the bus's progression from one stop to the next.

Once you have received and processed this file, your task is to answer users' questions about the bus routes. Specifically, when a user provides their current location (the departure point) and their desired destination, you are to analyze the data and suggest the most efficient bus route for the user to take.

Your answer should include the bus number the user should board, the departure stop, and the destination stop. The information you provide should be clear, concise, and communicated in a friendly and natural manner. Avoid providing overly detailed or prolonged explanations. 

Please note that users are only interested in knowing their departure stop and destination stop. Once the user reaches their destination stop, there's no need to provide additional information about the rest of the bus route.

Your suggested bus route is as follows:

**Bus Number**: 5
**Departure Stop**: Student Services Building
**Destination Stop**: Engineering Building
'''


def admin_view(request):
    context = {
        "bot_message": "Welcome to Texas A&M University! How can I assist you today?",
        "bot_avatar_url": settings.BOT_AVATAR_URL,
    }
    return render(request, 'admin.html', context)


def home_view(request):
    context = {
        "bot_message": "Welcome to Texas A&M University! How can I assist you today?",
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
        return JsonResponse({'error': 'There is no map'}, status=400)

    mapBus = prompt + read_file(path_file[0])

    MSGS.append(
        {"role": "system", 
        "content": mapBus,
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
