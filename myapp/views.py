import os
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
import openai
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from .forms import ContactusForm

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

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

@csrf_exempt
def chatPage(request):
    messages = []

    if request.method == 'POST':
        user_message = request.POST.get('message')

        if user_message:
            messages.append({'sender': 'user', 'content': user_message})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            response_message = response.choices[0].message['content']

            messages.append({'sender': 'api', 'content': response_message})
            return JsonResponse({'response': response_message})

    # Set default message for first visit
    default_message = "Hi, how can I help you?"

    return render(request, 'chatPage.html', {'messages': messages, 'default_message': default_message})





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
    if request.method == 'POST':
        form = ContactusForm(request.POST, request.FILES)  # Ensure request.FILES is included
        if form.is_valid():
            # Save the form data
            contactus_instance = form.save()

            # Prepare email data
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']
            from_email = form.cleaned_data['email']
            recipients = ['alobraessa2212@gmail.com']

            # Create the email
            email = EmailMessage(subject, message_body, from_email, recipients)

            # Attach image if available
            if contactus_instance.image:
                email.attach(contactus_instance.image.name, contactus_instance.image.read(), contactus_instance.image.content_type)

            try:
                # Send the email
                email.send()
                message = 'Message was sent successfully'
                hasError = False
            except Exception as e:
                # Handle exceptions and log errors
                message = f'Error sending message: {e}'
                hasError = True

            # Reset the form
            form = ContactusForm()
        else:
            message = 'Please make sure all fields are valid'
            hasError = True
    else:
        form = ContactusForm()
        message = ''
        hasError = False

    return render(request, 'contactus.html', {'form': form, 'message': message, 'hasError': hasError})



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



@login_required
def user_settings(request):
    if request.method == 'POST':
        user_form = UserChangeForm(instance=request.user, data=request.POST)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Important to keep the user logged in
            return redirect('user_settings')  # Redirect to the same page to show success

    else:
        user_form = UserChangeForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'user_settings.html', {
        'user_form': user_form,
        'password_form': password_form
    })

from .models import CommunityMessage
from .forms import CommunityMessageForm


@login_required
def community_chat(request):
    if request.method == 'POST':
        form = CommunityMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            return redirect('community_chat')  # Redirect to avoid resubmission on refresh
    else:
        form = CommunityMessageForm()

    messages = CommunityMessage.objects.all()
    return render(request, 'community_chat.html', {'form': form, 'messages': messages})