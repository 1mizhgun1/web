from django.contrib import admin
from django.urls import path

from front.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', GetQuestions, name='index_url'),
    path('hot/', GetBestQuestions, name='hot_url'),
    path('question/<str:id>/', GetQuestion, name='question_url'),
    path('ask/', RenderAskForm, name='ask_url'),
    path('tag/<str:tagname>/', GetQuestionsByTag, name='tag_url'),
    path('settings/', GetSettings, name='settings_url'),
    path('login/', RenderLoginForm, name='login_url'),
    path('register/', RenderRegisterForm, name='register_url'),
]
