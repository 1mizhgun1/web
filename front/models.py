from django.db import models
from django.contrib.auth.models import AbstractUser


# ==================================================================================================
# model managers


class QuestionManager(models.Manager):
    def best_questions(self):
        """Возвращает вопросы, отсортированные по убыванию количества лайков"""
        return super().get_queryset().order_by('-likes')
    
    def new_questions(self):
        """Возвращает вопросы, отсортированные от самого нового до самого старого"""
        return super().get_queryset().order_by('-send')
    
    def get_questions_by_tag(self, tag):
        """Возврашает QuerySet вопросов с тегом"""
        tag_links = Link_QuestionTag.objects.filter(tag=tag)
        return super().get_queryset().filter(id__in=tag_links.values_list('question__id', flat=True))
    

class TagManager(models.Manager):
    def popular_tags(self):
        """Возвращает теги, осортированные в порядке убывания количества вопросов, в которых они упомянуты"""
        return super().get_queryset().order_by('-questions')
    
    def get_tags_by_question(self, question):
        """Возвращает QuerySet тегов вопроса"""
        question_links = Link_QuestionTag.objects.filter(question=question)
        return super().get_queryset().filter(id__in=question_links.values_list('tag__id', flat=True))
    

class ProfileManager(models.Manager):
    def top_profiles(self):
        """Возращает пользователей отсортированных убыванию количества раз, когда их ответы кому-то помогли"""
        return super().get_queryset().order_by('-help_count')
    

class AnswerManager(models.Manager):
    def get_answers_by_question(self, question):
        """Возврашает QuerySet ответов на вопрос"""
        return Answer.objects.filter(question=question).order_by('-likes')
    

# ==================================================================================================
# models


class Profile(models.Model):
    objects = ProfileManager()

    avatar_filename = models.FilePathField(verbose_name='аватар')
    help_count = models.IntegerField(default=0, verbose_name='сколько раз помогли ответы этого пользователя')


class User(AbstractUser):
    # переопределение родительских полей
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь?')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал?')
    is_active = models.BooleanField(default=True, verbose_name='Активен?')
    date_joined = models.DateTimeField(auto_now=True, verbose_name='дата создания аккаунта')

    # добавление связи с профилем
    profile = models.OneToOneField(Profile, on_delete=models.PROTECT, verbose_name='id профиля')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


User.groups.field.remote_field.related_name = 'user_set_for_groups'
User.user_permissions.field.remote_field.related_name = 'user_set_for_permissions'


class Question(models.Model):
    objects = QuestionManager()

    title = models.CharField(max_length=256, verbose_name='заголовок')
    text = models.TextField(max_length=4096, verbose_name='текст')
    likes = models.IntegerField(default=0, verbose_name='количество лайков на вопросе')
    answers = models.IntegerField(default=0, verbose_name='количество ответов на вопрос')
    send = models.DateTimeField(auto_now=True, verbose_name='время отправки')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name='id профиля')
    

class Answer(models.Model):
    objects = AnswerManager()

    text = models.TextField(max_length=4096, verbose_name='текст')
    likes = models.IntegerField(default=0, verbose_name='количество лайков на ответе')
    help_count = models.IntegerField(default=0, verbose_name='сколько раз помог ответ')
    send = models.DateTimeField(auto_now=True, verbose_name='время отправки')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name='id профиля')
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name='id вопроса')


class Tag(models.Model):
    objects = TagManager()

    name = models.CharField(max_length=32, unique=True, verbose_name='имя')
    questions = models.IntegerField(default=0, verbose_name='количество вопросов с этим тегом')

    def __str__(self):
        return self.name
    
class Link_QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name='id вопроса')
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, verbose_name='id тега')

    class Meta:
        unique_together = (('question', 'tag'))


class QuestionLike(models.Model):
    send = models.DateTimeField(auto_now=True, verbose_name='время отправки')
    mark = models.IntegerField(choices=[(1, 'like'), (0, 'set_default'), (-1, 'dislike')], verbose_name='оценка')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name='id профиля')
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name='id вопроса')

    class Meta:
        unique_together = (('profile', 'question'))


class AnswerLike(models.Model):
    send = models.DateTimeField(auto_now=True, verbose_name='время отправки')
    mark = models.IntegerField(choices=[(1, 'like'), (0, 'set_default'), (-1, 'dislike')], verbose_name='оценка')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name='id профиля')
    answer = models.ForeignKey(Answer, on_delete=models.PROTECT, verbose_name='id ответа')

    class Meta:
        unique_together = (('profile', 'answer'))