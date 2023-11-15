from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from front.models import *
from typing import Union
import random


IS_LOG_IN = True            # влияет на юзерблок в хэдере
IS_WRONG_PASSWORD = True    # влияет на отображение ошибки в login.html
IS_WRONG_EMAIL = True       # влияет на отображение ошибки в signup.html


def getPageNumber(request: HttpRequest, total_pages: int) -> int:
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

    total_pages = queryset.count() // per_page
    if len(queryset) % per_page != 0:
        total_pages += 1
    
    page_number = getPageNumber(request, total_pages)

    return {
        'page_data': paginator.get_page(page_number),
        'current_page': page_number,
        'total_pages': total_pages,
    }


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


def getTemplateData():
    """Возвращает данные, необходимые для отображения шаблона всех страниц. Пока что данные пользователя захардкожены"""
    return {
        'log_in': IS_LOG_IN,
        'username': 'WEB 12',
        'login': 'homework',
        'email': 'web.12.vk@gmail.com',
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