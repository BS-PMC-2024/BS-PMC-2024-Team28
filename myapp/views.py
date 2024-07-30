import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import ContactusForm,SignupForm,UserProfileForm

from openai import OpenAI
from dotenv import load_dotenv
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.db import IntegrityError

from .models import UserProfile

load_dotenv()
API_KEY = 'sk-None-0ejjE5mfnMoSwR5utoBYT3BlbkFJD3x29ls1rCWodWXeRbfI'

# Create your views here.
@csrf_exempt
def chatPage(request):
    client = OpenAI()
    messages = []

    if request.method == 'POST':
        user_message = request.POST.get('message')

        if user_message:
            # Add user's message to the messages list
            messages.append({'sender': 'user', 'content': user_message})
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            response_message = response.choices[0].message.content


            # Prepare the data for the OpenAI API request
            # headers = {
            #     'Authorization': f'Bearer {API_KEY}',
            #     'Content-Type': 'application/json',
            # }
            # data = {
            #     'model': 'gpt-3.5-turbo',
            #     'messages': [{'role': 'user', 'content': user_message}],
            # }

















            # Make the API request
            # response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            # api_response = response.json()
            #
            # # Extract the API's response
            # if 'choices' in api_response and len(api_response['choices']) > 0:
            #     api_message = api_response['choices'][0]['message']['content']
            #     # Add API's response to the messages list
            #     messages.append({'sender': 'api', 'content': api_message})

    return render(request, 'chatPage.html', {'messages': messages})


@login_required
def logoutuser(request):
    logout(request)
    return redirect('loginuser')


def resetPassword(request):
    return render(request, 'resetPassword.html')


def signupuser(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('chatPage')
    else:
        form = SignupForm()
    return render(request, 'signupuser.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm

def loginuser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chatPage')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'loginuser.html', {'form': form})



def contactus(request):
    if request.method == 'GET':
        return render(request, 'contactus.html', {'form': ContactusForm()})
    else:
        form = ContactusForm(request.POST)
        if form.is_valid():
            form.save()
            message = 'Message was sent successfully'
            recipients = ['alobraessa2212@gmail.com']
            subject = request.POST.get('subject', '')
            message_body = request.POST.get('message', '')
            from_email = request.POST.get('email', '')
            send_mail(subject, message_body, from_email, recipients)
            form = ContactusForm()  # Reset the form after saving
        else:
            message = 'Please make sure all fields are valid'

        return render(request, 'contactus.html', {'form': form, 'message': message})


def base(request):
    return render(request,'base.html')


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {'form': form})

@login_required
def update_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'update_profile.html', {'form': form})