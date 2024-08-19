import os
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.core.mail import EmailMessage

from django.contrib.auth import login, logout, authenticate
from openai import OpenAIError

from .forms import ContactusForm,SignupForm,UserProfileForm

from .models import UserProfile

import os
import openai
from dotenv import load_dotenv
openai.api_key = os.getenv('sk-obSYJt7VRBNHBdKAfbgVRGYArY_m0AvloCcA2JfVBlT3BlbkFJaiMtlJi-aSit6lf3fJlztoDB4Gmhiauy6Hjbk2KRoA')

import openai
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Chat
#
# def ask_openai(message):
#     openai.api_key = 'sk-obSYJt7VRBNHBdKAfbgVRGYArY_m0AvloCcA2JfVBlT3BlbkFJaiMtlJi-aSit6lf3fJlztoDB4Gmhiauy6Hjbk2KRoA'
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": message},
#         ]
#     )
# #     answer = response.choices[0].message['content'].strip()
#     return answer

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')


def ask_openai(message, base64_image=None):
    # openai.api_key = 'sk-obSYJt7VRBNHBdKAfbgVRGYArY_m0AvloCcA2JfVBlT3BlbkFJaiMtlJi-aSit6lf3fJlztoDB4Gmhiauy6Hjbk2KRoA'
    client = OpenAI(
        api_key='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')

    if base64_image:
        message_content = [
            {"type": "text", "text": f"{message}"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                },
            },
        ]
    else:
        message_content = message

    message = {
        "role": "user",
        "content": message_content
    }
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[message]
    )
    print(completion.choices[0].message.content)

    answer = completion.choices[0].message.content
    return answer


def chatPage(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        image = request.FILES.get('image')
        base64_image = None
        if image:
            base64_image = encode_image(image)
        print(image)
        # base64_image = encode_image(image)
        print(base64_image)
        response = ask_openai(message, base64_image)
        print(response)
        # response_content = response['choices'][0]['message']['content']
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})

    chat_history = Chat.objects.all()
    context = {
        'chat_history': chat_history
    }
    # return render(request, 'chatPage.html', {'chats': chats})
    return render(request, 'chatPage.html', context)

@login_required
def chat_history(request):
    user = request.user
    chats = Chat.objects.filter(user=user).order_by('created_at')

    grouped_chats = defaultdict(list)
    for chat in chats:
        date = chat.created_at.strftime('%Y-%m-%d')
        grouped_chats[date].append({
            'id': chat.id,
            'message': chat.message,
            'response': chat.response,
            'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    sorted_grouped_chats = sorted(grouped_chats.items(), reverse=True)

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
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=request.user.userprofile)

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