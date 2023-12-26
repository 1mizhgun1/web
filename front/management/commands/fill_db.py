from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.db import transaction
from front.models import *

from faker import Faker
import random
import pytz
import time


fake = Faker(['ru_RU', 'en_US'])

with open('front/management/commands/words.txt', 'r') as file:
    english_words = [line.strip("\n") for line in file.readlines()]


def _genArrayOfUniqueRandomWords(count: int) -> list[str]:
    """Генеирует массив из count различных слов"""
    result = set()
    while len(result) < count:
        result.add(random.choice(english_words))
    return list(result)


def _genArrayOfUniqueRandomIntegerPairs(count: int, max_value_1: int, max_value_2: int) -> list:
    """Генерирует массив из count различных пар чисел, либо все возможные пары, если их количество меньше count"""
    result = set()
    while len(result) < min((max_value_1 + 1) * (max_value_2 + 1), count):
        result.add((random.randint(0, max_value_1), random.randint(0, max_value_2)))
    return list(result)


def getTime(start_time) -> str:
    """Нужна для вывода прошедшего времени"""
    return f'Time spent: {round(time.time() - start_time, 2)} seconds'


def getEndOfLine(chunk_count: int, chunk: int) -> str:
    """Нужна для определения того, откуда начинать писать следующую строку"""
    return '\r' if chunk <= chunk_count - 2 else '\n'


class Command(BaseCommand):
    help = 'Заполняет базу данных случайными данными'

    def add_arguments(self, parser):
        """Считывает аргумент ratio - количество пользователей"""
        parser.add_argument('ratio', type=int, help='Количество пользователей для добавления')    

    def handle(self, *args, **kwargs):
        """
        При ratio = 100 работает за 20 секунд
        При ratio = 1000 работает за 2 минуты
        При ratio = 10000 работает за 25 минут
        """

        # считываем ratio - количество пользователей
        ratio = kwargs['ratio']

        self.stdout.write(self.style.SUCCESS('STARTED!'))
        global_start_time = time.time()

        # генерация профилей
        start_time = time.time()
        profiles = [
            Profile() for i in range(ratio)
        ]
        with transaction.atomic():
            Profile.objects.bulk_create(profiles)
        self.stdout.write(self.style.SUCCESS(f'Profiles - created {ratio}. {getTime(start_time)}'))

        # генерация пользователей
        start_time = time.time()
        usernames = [fake.unique.user_name() for i in range(ratio)]
        users = [
            User(
                username = usernames[i],
                password = hash(fake.password(length=random.randint(8, 32))),
                first_name = fake.first_name(),
                last_name = fake.last_name(),
                email = fake.email(),
                last_login = str(fake.date_time_between_dates(datetime_start='-365d', datetime_end='-1d', tzinfo=pytz.UTC)),
                date_joined = str(fake.date_time_between_dates(datetime_start='-365d', datetime_end='-1d', tzinfo=pytz.UTC)),
                profile = profiles[i]
            ) for i in range(ratio)
        ]
        with transaction.atomic():
            User.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS(f'Users - created {ratio}. {getTime(start_time)}'))

        # генерация вопросов
        start_time = time.time()
        questions = [
            Question(
                title = fake.sentence(nb_words=12),
                text = fake.paragraph(nb_sentences=10),
                send = str(fake.date_time_between_dates(datetime_start='-365d', datetime_end='-1d', tzinfo=pytz.UTC)),
                profile = random.choice(profiles)
            ) for i in range(ratio * 10)
        ]
        with transaction.atomic():
            Question.objects.bulk_create(questions)
        self.stdout.write(self.style.SUCCESS(f'Questions - created {ratio * 10}. {getTime(start_time)}'))

        # генерация тегов
        start_time = time.time()
        tag_names = _genArrayOfUniqueRandomWords(ratio)
        tags = []
        for i in range(ratio):
            tags.append(Tag(
                name = tag_names[i]
            ))
            
        with transaction.atomic():
            Tag.objects.bulk_create(tags)
        self.stdout.write(self.style.SUCCESS(f'Tags - created {ratio}. {getTime(start_time)}'))

        # генерация связей между вопросами и тегами
        start_time = time.time()
        flag = True
        link_params = _genArrayOfUniqueRandomIntegerPairs(ratio * 30, ratio * 10 - 1, ratio - 1)
        for chunk in range(30):
            if flag == False:
                break
            links = []
            for i in range(ratio):
                if chunk * ratio + i >= len(link_params):
                    flag = False
                    break
                links.append(Link_QuestionTag(
                    question = questions[link_params[chunk * ratio + i][0]],
                    tag = tags[link_params[chunk * ratio + i][1]]
                ))
            with transaction.atomic():
                Link_QuestionTag.objects.bulk_create(links)
            self.stdout.write(self.style.SUCCESS(f'Links Questions-Tags - created {min(len(link_params), ratio * (chunk + 1))}. {getTime(start_time)}{getEndOfLine(30, chunk)}'), ending='')

        # генерация лайков на вопросы
        start_time = time.time()
        flag = True
        question_like_params = _genArrayOfUniqueRandomIntegerPairs(ratio * 50, ratio - 1, ratio * 10 - 1)
        for chunk in range(50):
            if flag == False:
                break
            question_likes = []
            for i in range(ratio):
                if chunk * ratio + i >= len(question_like_params):
                    flag = False
                    break
                question_likes.append(QuestionLike(
                    mark = random.choice([1] * 9 + [-1]),
                    profile = profiles[question_like_params[chunk * ratio + i][0]],
                    question = questions[question_like_params[chunk * ratio + i][1]]
                ))
            with transaction.atomic():
                QuestionLike.objects.bulk_create(question_likes)
            self.stdout.write(self.style.SUCCESS(f'Question Likes - created {ratio * (chunk + 1)}. {getTime(start_time)}{getEndOfLine(50, chunk)}'), ending='')

        # заполнение Answer, Answer Like, а также подсчёт числа лайков на ответах
        start_time = time.time()
        for chunk in range(100):
            answers: list[Answer] = []
            for i in range(ratio):
                answers.append(Answer(
                    text = fake.paragraph(nb_sentences=5),
                    is_right = random.choice([True, False, False, False, False, False]),
                    send = str(fake.date_time_between_dates(datetime_start='-365d', datetime_end='-1d', tzinfo=pytz.UTC)),
                    profile = random.choice(profiles),
                    question = random.choice(questions)
                ))
               
            answer_like_params = _genArrayOfUniqueRandomIntegerPairs(ratio * 2, ratio - 1, ratio - 1)
            answer_likes: list[AnswerLike] = []
            for i in range(min(ratio * 2, len(answer_like_params))):
                current_mark = random.choice([1] * 9 + [-1])
                answer_likes.append(AnswerLike(
                    mark = current_mark,
                    profile = profiles[answer_like_params[i][0]],
                    answer = answers[answer_like_params[i][1]]
                ))
                answers[answer_like_params[i][1]].likes += current_mark

            with transaction.atomic():
                Answer.objects.bulk_create(answers)
                AnswerLike.objects.bulk_create(answer_likes)
            self.stdout.write(self.style.SUCCESS(f'Answers - created {ratio * (chunk + 1)}. Answer likes - created {2 * ratio * (chunk + 1)}. {getTime(start_time)}{getEndOfLine(100, chunk)}'), ending='')

        # заполнение счётчиков - сколько лайков собрали ответы пользователя
        start_time = time.time()
        for profile in profiles:
            profile.likes = Answer.objects.filter(profile_id=profile.pk).aggregate(Sum('likes'))['likes__sum']
        with transaction.atomic():
            Profile.objects.bulk_update(profiles, fields=['likes'])
        self.stdout.write(self.style.SUCCESS(f'Profile counters - counted. {getTime(start_time)}'))

        # заполнение счётчиков - сколько раз тег упомянут в вопросах
        start_time = time.time()
        for tag in tags:
            tag.questions = Link_QuestionTag.objects.filter(tag_id=tag.pk).count()
        with transaction.atomic():
            Tag.objects.bulk_update(tags, fields=['questions'])
        self.stdout.write(self.style.SUCCESS(f'Tag counters - counted. {getTime(start_time)}'))

        # заполнение счётчиков - сколько лайков и ответов у вопроса
        start_time = time.time()
        for chunk in range(10):
            chunk_questions = questions[chunk * ratio : (chunk + 1) * ratio]
            for question in chunk_questions:
                question_likes = QuestionLike.objects.filter(question_id=question.pk).aggregate(Sum('mark'))['mark__sum']
                question.likes = question_likes if question_likes else 0
                question.answers = Answer.objects.filter(question_id=question.pk).count()
            with transaction.atomic():
                Question.objects.bulk_update(chunk_questions, fields=['likes', 'answers'])
            self.stdout.write(self.style.SUCCESS(f'Question likes counters - counted {ratio * (chunk + 1)}. {getTime(start_time)}{getEndOfLine(10, chunk)}'), ending='')

        self.stdout.write(self.style.SUCCESS(f'SUCCESS! Total time: {time.time() - global_start_time}'))