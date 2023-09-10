from django.shortcuts import render
from django.http import JsonResponse


def home(request):
    return render(request, 'home.html')


def submit(request):
    messages = request.POST.getlist("messages[]")

    print(messages)

    data = {"message": messages}
    return JsonResponse(data)