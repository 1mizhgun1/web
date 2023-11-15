from django.core.management.base import BaseCommand
from front.models import *
import time


class Command(BaseCommand):
    help = 'Очищает все таблицы базы данных'

    def handle(self, *args, **kwargs):
        start_time = time.time()

        QuestionLike.objects.all().delete()
        AnswerLike.objects.all().delete()
        Link_QuestionTag.objects.all().delete()
        Tag.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        User.objects.all().delete()
        Profile.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'SUCCESS! Total time: {time.time() - start_time}'))