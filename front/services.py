from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
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


def getPopularTags():
    """Возвращает данные о популярных тегах в том виде, в котором они нужны HTML-шаблону"""
    return [
        {
            'tag': tag.name,
            'color': random.choice(['success', 'primary', 'warning', 'danger', 'secondary'])
        } for tag in Tag.objects.popular_tags()[:15]
    ]


def getTopMembers():
    """Возвращает данные о топ-пользователях в том виде, в котором они нужны HTML-шаблону"""
    top_members = []
    for member in Profile.objects.top_profiles()[:10]:
        current_user = User.objects.get(profile=member)
        top_members.append({
            'username': current_user.username,
            'display_name': current_user.first_name + ' ' + current_user.last_name
        })
    return top_members


def getUserData(user: User):
    """Возвращает данные, необходимые для отображения юзерблока"""
    if isinstance(user, AnonymousUser):
        return {
            'log_in': False,
        }
    
    return {
        'log_in': user.is_authenticated,
        'first_name': user.first_name,
        'avatar_filename': Profile.objects.get(user=user).avatar_filename,
    }


def getTemplateData(request: HttpRequest):
    """Возвращает данные, необходимые для отображения шаблона всех страниц"""
    return {
        'user': getUserData(request.user),
        'tags': getPopularTags(),
        'members': getTopMembers()
    }


def getAvatarFilename(entity: Union[Question, Answer]) -> str:
    """Возвращает название файла аватарки вопроса либо ответа"""
    profile = get_object_or_404(Profile, pk=entity.profile_id)
    return profile.avatar_filename


def addTags(questions: list[Question]) -> None:
    """добавляет теги к вопросам"""
    for question in questions:
        question.tags = Tag.objects.get_tags_by_question(question)


def addAvatarFilename(entities: list[Union[Question, Answer]]) -> None:
    """добавляет названия файлов с аватарками к вопросам либо ответам"""
    for entity in entities:
        entity.avatar_filename = getAvatarFilename(entity)


def addData_ToQuestions(questions: Union[list[Question], Question]) -> None:
    """добавляет к вопросу/вопросам данные, которые нужны для отображения"""
    if isinstance(questions, Question):
        addTags([questions])
        addAvatarFilename([questions])
    else:
        addTags(questions)
        addAvatarFilename(questions)


def addData_ToAnswers(answers: Union[list[Answer], Answer]) -> None:
    """добавляет к ответу/ответам данные, которые нужны для отображения"""
    if isinstance(answers, Answer):
        addAvatarFilename([answers])
    else:
        addAvatarFilename(answers)


def show404(message: str) -> HttpResponse:
    """Отображает ошибку 404"""
    return HttpResponse(f'''
        <div style="height: 50%; position: relative; transform: translateY(-33%); top: 50%; text-align: center;">
            <h1 style="font-size: 48px; font-weight: 500;">ERROR 404 - not found</h1>
            <h1 style="font-weight: 500">{message}</h1>
            <a href="/"><h1 style="font-weight: 500">На главную</h1></a>
        </div>
    ''')