from django.contrib import admin
from django.urls import path

from front.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', GetQuestions, name='index_url'),
    path('hot/', GetBestQuestions, name='hot_url'),
    path('question/<str:id>/', GetQuestion, name='question_url'),
    path('ask/', ask, name='ask_url'),
    path('tag/<str:tagname>/', GetQuestionsByTag, name='tag_url'),
    path('profile/edit/', GetSettings, name='settings_url'),
    path('login/', log_in, name='login_url'),
    path('logout/', log_out, name='logout_url'),
    path('signup/', sign_up, name='register_url'),
]
