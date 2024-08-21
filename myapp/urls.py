from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

 # path('', views.chatPage, name='chatPage'),
path('', views.chatPage, name='chatPage'),
# Add a URL for contactus success page
path('contactus-success/', views.contactus_success, name='contactus_success'),

 path('reset/', views.resetPassword, name='resetPassword'),
 path('chat-history/', views.chat_history, name='chat_history'),
 path('base/', views.base, name='base'),
 path('contactus/', views.contactus, name='contactus'),
 path('signup/', views.signupuser, name='signupuser'),
 path('login/', views.loginuser, name='loginuser'),
 path('logout/', views.logoutuser, name='logoutuser'),
 # path('profile/', views.profile, name='profile'),
 # path('profile/update/', views.update_profile, name='update_profile'),
path('profile/', views.profile, name='profile'),
path('profile/update/', views.update_profile, name='update_profile'),

 # path('settings/', views.user_settings, name='user_settings'),
path('settings/', views.user_settings, name='user_settings'),

 # path('community/', views.community_chat, name='community_chat'),
path('community/', views.community_chat, name='community_chat'),



        ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

