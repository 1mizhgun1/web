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
        """Возращает пользователей отсортированных убыванию количества лайков, которое собрал их профиль"""
        return super().get_queryset().order_by('-likes')
    

class AnswerManager(models.Manager):
    def get_answers_by_question(self, question):
        """Возврашает QuerySet ответов на вопрос"""
        return Answer.objects.filter(question=question).order_by('-likes')
    
    def process_right(self, answer):
        """Обрабатывает переключение отметки о том, что ответ верный"""
        if answer.is_right:
            answer.is_right = False
        else:
            answer.is_right = True
        answer.save()
    
    
class LikeManager(models.Manager):
    def process_like(self, entity, mark, user):
        """Обрабатывает нажатие на кнопки лайка и дизлайка. Функция возрващет:
        0 - теперь нет ни лайка, ни дизлайка
        -1 - есть дизлайк
        1 - есть лайк"""
        if isinstance(entity, Question):
            like_entities = super().get_queryset().filter(question=entity).filter(profile=user.profile)
        else:
            like_entities = super().get_queryset().filter(answer=entity).filter(profile=user.profile)
        likes = like_entities.filter(mark=mark)
        neytral = like_entities.filter(mark=0)
        dislikes = like_entities.filter(mark=-mark)
        if not like_entities.exists():
            if isinstance(entity, Question):
                super().get_queryset().create(
                    mark=mark,
                    profile=user.profile,
                    question=entity
                )
            else:
                super().get_queryset().create(
                    mark=mark,
                    profile=user.profile,
                    answer=entity
                )
            entity.likes += mark
            result = mark
        else:
            if likes.exists():
                current = likes.first()
                current.mark = 0
                entity.likes -= mark
                result = 0
            elif neytral.exists():
                current = neytral.first()
                current.mark = mark
                entity.likes += mark
                result = mark
            else:
                current = dislikes.first()
                current.mark = mark
                entity.likes += 2 * mark
                result = mark
            current.save()
        entity.save()
        return result
    

# ==================================================================================================
# models


class Profile(models.Model):
    objects = ProfileManager()

    avatar = models.ImageField(default='ava.jpg', upload_to='avatar/%Y/%m/%d', verbose_name='аватар', null=True, blank=True)
    likes = models.IntegerField(default=0, verbose_name='сколько лайков собрали ответы этого пользователя')


class User(AbstractUser):
    # переопределение родительских полей
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь?')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал?')
    is_active = models.BooleanField(default=True, verbose_name='Активен?')
    date_joined = models.DateTimeField(auto_now=True, verbose_name='дата создания аккаунта')

    # добавление связи с профилем
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='id профиля')

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
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='id профиля')
    

class Answer(models.Model):
    objects = AnswerManager()

    text = models.TextField(max_length=4096, verbose_name='текст')
    likes = models.IntegerField(default=0, verbose_name='количество лайков на ответе')
    is_right = models.BooleanField(default=False, verbose_name='отмечен ли ответ как верный')
    send = models.DateTimeField(auto_now=True, verbose_name='время отправки')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='id профиля')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='id вопроса')


class Tag(models.Model):
    objects = TagManager()

    name = models.CharField(max_length=32, unique=True, verbose_name='имя')
    questions = models.IntegerField(default=0, verbose_name='количество вопросов с этим тегом')

    def __str__(self):
        return self.name
    
class Link_QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='id вопроса')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='id тега')

    class Meta:
        unique_together = (('question', 'tag'))


class QuestionLike(models.Model):
    objects = LikeManager()
    
    send = models.DateTimeField(auto_now=True, verbose_name='время отправки')
    mark = models.IntegerField(choices=[(1, 'like'), (0, 'set_default'), (-1, 'dislike')], verbose_name='оценка')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='id профиля')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='id вопроса')

    class Meta:
        unique_together = (('profile', 'question'))


class AnswerLike(models.Model):
    objects = LikeManager()
    
    send = models.DateTimeField(auto_now=True, verbose_name='время отправки')
    mark = models.IntegerField(choices=[(1, 'like'), (0, 'set_default'), (-1, 'dislike')], verbose_name='оценка')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='id профиля')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='id ответа')

    class Meta:
        unique_together = (('profile', 'answer'))