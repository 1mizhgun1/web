from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Link_QuestionTag)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)
