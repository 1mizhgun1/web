from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from front.models import *
from typing import Union
import random


def getValidPageNumber(request: HttpRequest, total_pages: int) -> int:
    """Возращает валидный номер текущей страницы"""
    try:
        page_number = int(request.GET.get('page'))
        if page_number < 1:
            return 1
        elif page_number > total_pages:
            return total_pages
        return page_number
    except:
        return 1


def paginate(queryset: models.QuerySet, request: HttpRequest, per_page: int = 5) -> dict:
    """Возвращает данные текущей страницы, а также общие сведения о страницах"""
    paginator = Paginator(queryset, per_page)

    total_pages = paginator.num_pages
    page_number = getValidPageNumber(request, total_pages)

    return {
        'page_data': paginator.get_page(page_number),
        'current_page': page_number,
        'total_pages': total_pages,
    }


def getPageNumber(queryset: models.QuerySet, pk: int, per_page: int = 5) -> int:
    """Возвращает номер страницы, на котором находится объект с первичным ключом pk"""
    paginator = Paginator(queryset, per_page)
    for page_number in range(paginator.num_pages, 0, -1):
        if pk in [item.pk for item in paginator.get_page(page_number)]:
            return page_number
    return 1


def cache_popular_tags():
    cache_key = 'popular_tags'
    tags = [
        {
            'tag': tag.name,
            'color': random.choice(['success', 'primary', 'warning', 'danger', 'secondary'])
        } for tag in Tag.objects.popular_tags()[:15]
    ]
    cache.set(cache_key, tags, 30)


def getPopularTags():
    """Возвращает данные о популярных тегах в том виде, в котором они нужны HTML-шаблону"""
    cache_key = 'popular_tags'
    return cache.get(cache_key)    


def cache_top_members():
    cache_key = 'top_members'
    top_members = []
    for member in Profile.objects.top_profiles()[:10]:
        current_user = User.objects.get(profile=member)
        top_members.append({
            'username': current_user.username,
            'display_name': current_user.first_name + ' ' + current_user.last_name
        })
    cache.set(cache_key, top_members, 30)


def getTopMembers():
    """Возвращает данные о топ-пользователях в том виде, в котором они нужны HTML-шаблону"""
    cache_key = 'top_members'
    return cache.get(cache_key)


def getUserData(user: User):
    """Возвращает данные, необходимые для отображения юзерблока"""
    if isinstance(user, AnonymousUser):
        return {
            'log_in': False,
        }
    
    return {
        'log_in': user.is_authenticated,
        'first_name': user.first_name,
        'avatar_url': Profile.objects.get(user=user).avatar.url,
    }


def getTemplateData(request: HttpRequest):
    """Возвращает данные, необходимые для отображения шаблона всех страниц"""
    return {
        'user': getUserData(request.user),
        'tags': getPopularTags(),
        'members': getTopMembers()
    }


def getAvatarUrl(entity: Union[Question, Answer]) -> str:
    """Возвращает ссылку на аватарку вопроса либо ответа"""
    profile = get_object_or_404(Profile, pk=entity.profile_id)
    return profile.avatar.url


def checkIsAsker(user: User, question: Question) -> bool:
    """Проверает, этому ли пользователю принадлежит вопрос"""
    if isinstance(user, AnonymousUser):
        return False
    return question.profile == user.profile


def checkIsMarked(user: User, entity: Union[Question, Answer]) -> tuple:
    """Проверяет, есть ли лайк или дизлайк на вопросе/ответе"""
    if isinstance(user, AnonymousUser):
        return (False, False)
    
    if isinstance(entity, Question):
        like_entities = QuestionLike.objects.filter(question=entity).filter(profile=user.profile)
    else:
        like_entities = AnswerLike.objects.filter(answer=entity).filter(profile=user.profile)
    likes = like_entities.filter(mark=1)
    dislikes = like_entities.filter(mark=-1)
    return (likes.exists(), dislikes.exists())


def addTags(questions: list[Question]) -> None:
    """добавляет теги к вопросам"""
    for question in questions:
        question.tags = Tag.objects.get_tags_by_question(question)


def addAvatarUrl(entities: list[Union[Question, Answer]]) -> None:
    """добавляет ссылки на аватарки к вопросам либо ответам"""
    for entity in entities:
        entity.avatar_url = getAvatarUrl(entity)
        
        
def addMarkInfo(user: User, entities: list[Union[Question, Answer]]) -> None:
    """добавляет сведения о лайках к вопросам либо ответам"""
    for entity in entities:
        info = checkIsMarked(user, entity)
        entity.liked = info[0]
        entity.disliked = info[1]


def addData_ToQuestions(user: User, questions: Union[list[Question], Question]) -> None:
    """добавляет к вопросу/вопросам данные, которые нужны для отображения"""
    if isinstance(questions, Question):
        addTags([questions])
        addAvatarUrl([questions])
        addMarkInfo(user, [questions])
    else:
        addTags(questions)
        addAvatarUrl(questions)
        addMarkInfo(user, questions)


def addData_ToAnswers(user: User, answers: Union[list[Answer], Answer]) -> None:
    """добавляет к ответу/ответам данные, которые нужны для отображения"""
    if isinstance(answers, Answer):
        addAvatarUrl([answers])
        addMarkInfo(user, [answers])
    else:
        addAvatarUrl(answers)
        addMarkInfo(user, answers)


def show404(message: str) -> HttpResponse:
    """Отображает ошибку 404"""
    return HttpResponse(f'''
        <div style="height: 50%; position: relative; transform: translateY(-33%); top: 50%; text-align: center;">
            <h1 style="font-size: 48px; font-weight: 500;">ERROR 404 - not found</h1>
            <h1 style="font-weight: 500">{message}</h1>
            <a href="/"><h1 style="font-weight: 500">На главную</h1></a>
        </div>
    ''')