from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

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
    path('question_like/', question_like, name='question_like_url'),
    path('answer_like/', answer_like, name='answer_like_url'),
    path('answer_right/', answer_right, name='answer_right_url'),
    path('send_answer/<int:question_id>/', send_answer, name='send_answer'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
