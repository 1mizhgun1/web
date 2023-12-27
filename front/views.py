from django.forms import model_to_dict
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.conf import settings as config

from front.models import *
from front.services import *
from front.forms import *

import jwt
import time

from cent import Client


client = Client(config.CENTRIFUGO_API_URL, api_key=config.CENTRIFUGO_API_KEY, timeout=1)


def getCentrifugoData(user_id: int, channel: str):
    token = jwt.encode({"sub": str(user_id), "exp": int(time.time()) + 10*60}, config.CENTRUFUGO_TOKEN_HMAC_SECRET_KEY, algorithm="HS256")
    print(user_id, token)
    return {
        'centrifugo': {
            'token': token,
            'ws_url': config.CENTRIFUGO_URL,
            'channel': channel,
        }
    }


def GetQuestions(request: HttpRequest):
    """Отображает страницу новых вопросов"""
    page_of_questions = paginate(Question.objects.new_questions(), request)
    addData_ToQuestions(request.user, page_of_questions['page_data'])

    return render(request, 'index.html', {
        'template': getTemplateData(request),
        'questions': page_of_questions['page_data'],
        'current_page': page_of_questions['current_page'],
        'pages': page_of_questions['total_pages'],
        'tag': '',
        'mode': 'new',
    })


def GetBestQuestions(request: HttpRequest):
    """Отображает страницу топ-вопросов"""
    page_of_questions = paginate(Question.objects.best_questions(), request)
    addData_ToQuestions(request.user, page_of_questions['page_data'])

    return render(request, 'index.html', {
        'template': getTemplateData(request),
        'questions': page_of_questions['page_data'],
        'current_page': page_of_questions['current_page'],
        'pages': page_of_questions['total_pages'],
        'tag': '',
        'mode': 'best',
    })


def GetQuestionsByTag(request: HttpRequest, tagname: str):
    """Отображает страницу вопросов по тегу"""
    try:
        tag = get_object_or_404(Tag, name=tagname)
    except Http404:
        return show404(f'There is no tag "{tagname}"')

    questions_with_tag = Question.objects.get_questions_by_tag(tag)
    page_of_questions = paginate(questions_with_tag, request)
    addData_ToQuestions(request.user, page_of_questions['page_data'])

    return render(request, 'index.html', {
        'template': getTemplateData(request),
        'questions': page_of_questions['page_data'],
        'current_page': page_of_questions['current_page'],
        'pages': page_of_questions['total_pages'],
        'tag': tagname,
        'mode': 'tag',
    })


@csrf_protect
@login_required(login_url='/login/', redirect_field_name='continue')
def send_answer(request: HttpRequest, question_id: int):
    """Обрабатывает отправку ответа на вопрос"""
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=question_id)
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(request.user, question)
            client.publish(f'question.{question_id}', model_to_dict(answer))
            return JsonResponse({
                'status': 'success',
                'pk': answer.pk,
                'text': answer.text,
                'avatar_url': Profile.objects.get(user=request.user).avatar.url,
                'likes': answer.likes,
                'is_owner': checkIsAsker(request.user, question),
            })
    return JsonResponse({'status': 'error'})


def GetQuestion(request: HttpRequest, id: int):
    """Отображает страницу одного вопроса"""
    try:
        question = get_object_or_404(Question, pk=id)
    except:
        return show404(f'There is no question with id = {id}')
    addData_ToQuestions(request.user, question)

    answers = Answer.objects.get_answers_by_question(question)
    page_of_answers = paginate(answers, request, 2)
    addData_ToAnswers(request.user, page_of_answers['page_data'])

    answer_form = AnswerForm()
    # return redirect(f'{reverse("question_url", kwargs={"id": id})}?page={getPageNumber(answers, answer.pk)}')

    return render(request, 'question.html', {
        'template': getTemplateData(request),
        'question': question,
        'answers': page_of_answers['page_data'],
        'current_page': page_of_answers['current_page'],
        'pages': page_of_answers['total_pages'],
        'form': answer_form,
        'is_owner': checkIsAsker(request.user, question),
        **getCentrifugoData(request.user.pk, f'question.{id}'),
    })


@csrf_protect
@login_required(login_url='/login/', redirect_field_name='continue')
def GetSettings(request: HttpRequest):
    """Обработка формы изменения настроек"""
    settings_form = SettingsForm()
    if request.method == 'GET':
        settings_form.initFields(request.user)
    elif request.method == 'POST':
        settings_form = SettingsForm(request.POST, request.FILES)
        if settings_form.is_valid():
            settings_form.save(request.user)
            return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'settings.html', {
        'template': getTemplateData(request),
        'form': settings_form,
    })


@csrf_protect
@login_required(login_url='/login/', redirect_field_name='continue')
def ask(request: HttpRequest):
    """Обработка формы отправки вопроса"""
    ask_form = AskForm()
    if request.method == 'POST':
        ask_form = AskForm(request.POST)
        if ask_form.is_valid():
            question = ask_form.save(request.user)
            return redirect(reverse('question_url', kwargs={'id': question.pk}))

    return render(request, 'ask.html', {
        'template': getTemplateData(request),
        'form': ask_form,
    })


def log_in(request: HttpRequest):
    """Отбработка формы входа в аккаунт"""
    login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user:
                login(request, user)
                return redirect(request.GET.get('continue', reverse('index_url')))
            else:
                login_form.add_error(None, "Wrong login or password")
                login_form.add_error('username', '')
                login_form.add_error('password', '')
    
    return render(request, 'login.html', {
        'template': getTemplateData(request),
        'form': login_form,
    })


@csrf_protect
@login_required(login_url='/login/', redirect_field_name='continue')
def log_out(request: HttpRequest):
    """Обработка выхода из аккаунта"""
    logout(request)
    return redirect(request.META.get('HTTP_REFERER'))


def sign_up(request: HttpRequest):
    """Обработка регистрации"""
    register_form = RegisterForm()
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save()
            if user:
                return redirect(reverse('index_url'))

    return render(request, 'signup.html', {
        'template': getTemplateData(request),
        'form': register_form,
    })
    

@csrf_protect
@login_required(login_url='/login/', redirect_field_name='continue')
def question_like(request: HttpRequest):
    """Обработка лайка на вопрос"""   
    id = request.POST.get('question_id')
    try:
        mark = int(request.POST.get('mark'))
    except:
        return show404(f'Invalid request')
    question = get_object_or_404(Question, pk=id)
    result = QuestionLike.objects.process_like(question, mark, request.user)
    return JsonResponse({'likes': question.likes, 'result': result})


@csrf_protect
@login_required(login_url='/login/', redirect_field_name='continue')
def answer_like(request):
    """Обработка лайка на ответ"""
    id = request.POST.get('answer_id')
    try:
        mark = int(request.POST.get('mark'))
    except:
        return show404('Invalid request')
    answer = get_object_or_404(Answer, pk=id)
    result = AnswerLike.objects.process_like(answer, mark, request.user)
    return JsonResponse({'likes': answer.likes, 'result': result})


@csrf_protect
@login_required(login_url='/login/', redirect_field_name='continue')
def answer_right(request):
    """Обработка отметки того, что ответ верный"""
    id = request.POST.get('answer_id')
    answer = get_object_or_404(Answer, pk=id)
    if checkIsAsker(request.user, answer.question):
        Answer.objects.process_right(answer)
    return JsonResponse({'is_right': answer.is_right})
