from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from front.models import *
from front.services import *


def GetQuestions(request):
    """Отображает страницу новых вопросов"""
    page_of_questions = paginate(Question.objects.new_questions(), request)
    addData_ToQuestions(page_of_questions['page_data'])

    return render(request, 'index.html', {
        'template': getTemplateData(),
        'questions': page_of_questions['page_data'],
        'current_page': page_of_questions['current_page'],
        'pages': page_of_questions['total_pages'],
        'tag': '',
        'mode': 'new',
    })


def GetBestQuestions(request):
    """Отображает страницу топ-вопросов"""
    page_of_questions = paginate(Question.objects.best_questions(), request)
    addData_ToQuestions(page_of_questions['page_data'])

    return render(request, 'index.html', {
        'template': getTemplateData(),
        'questions': page_of_questions['page_data'],
        'current_page': page_of_questions['current_page'],
        'pages': page_of_questions['total_pages'],
        'tag': '',
        'mode': 'best',
    })


def GetQuestionsByTag(request, tagname: str):
    """Отображает страницу вопросов по тегу"""
    try:
        tag = get_object_or_404(Tag, name=tagname)
    except Http404:
        return show404(f'There is no tag "{tagname}"')

    questions_with_tag = Question.objects.get_questions_by_tag(tag)
    page_of_questions = paginate(questions_with_tag, request)
    addData_ToQuestions(page_of_questions['page_data'])

    return render(request, 'index.html', {
        'template': getTemplateData(),
        'questions': page_of_questions['page_data'],
        'current_page': page_of_questions['current_page'],
        'pages': page_of_questions['total_pages'],
        'tag': tagname,
        'mode': 'tag',
    })


def GetQuestion(request, id: int):
    """Отображает страницу одного вопроса"""
    try:
        question = get_object_or_404(Question, pk=id)
    except:
        return show404(f'There is no question with id = {id}')
    addData_ToQuestions(question)

    answers = Answer.objects.get_answers_by_question(question)
    page_of_answers = paginate(answers, request)
    addData_ToAnswers(page_of_answers['page_data'])

    return render(request, 'question.html', {
        'template': getTemplateData(),
        'question': question,
        'answers': page_of_answers['page_data'],
        'current_page': page_of_answers['current_page'],
        'pages': page_of_answers['total_pages'],
    })


def GetSettings(request):
    """Отображает страницу настроек"""
    return render(request, 'settings.html', {
        'template': getTemplateData(),
    })


def RenderAskForm(request):
    """Отображает форму создания вопроса"""
    return render(request, 'ask.html', {
        'template': getTemplateData(),
    })


def RenderLoginForm(request):
    """Отображает форму авторизации"""
    return render(request, 'login.html', {
        'template': getTemplateData(),
        'is_wrong_password': IS_WRONG_PASSWORD,
    })


def RenderRegisterForm(request):
    """Отображает форму регистрации"""
    return render(request, 'signup.html', {
        'template': getTemplateData(),
        'is_wrong_email': IS_WRONG_EMAIL,
    })