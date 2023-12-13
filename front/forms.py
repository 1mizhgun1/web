from django import forms
from .models import *

from QA.settings import BASE_DIR
import os


USERNAME_MIN_LENGTH = 3
PASSWORD_MIN_LENGTH = 8
TAG_MAX_LENGTH = 32


class LoginForm(forms.Form):
    """Класс, отвечающий за форму входа в аккаунт"""
    username = forms.CharField()
    password = forms.CharField(min_length=PASSWORD_MIN_LENGTH, widget=forms.PasswordInput)
    

class RegisterForm(forms.Form):
    """Класс, отвечающий за форму регистрации"""
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField(widget=forms.EmailInput)
    username = forms.CharField(min_length=USERNAME_MIN_LENGTH)
    password = forms.CharField(min_length=PASSWORD_MIN_LENGTH, widget=forms.PasswordInput)
    password_again = forms.CharField(min_length=PASSWORD_MIN_LENGTH, widget=forms.PasswordInput)

    def clean(self):
        """Валидирует форму"""
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            self.add_error('username', 'This user name is already taken')
        if self.cleaned_data['password'] != self.cleaned_data['password_again']:
            self.add_error('password', '')
            self.add_error('password_again', 'Passwords don`t match')
        
    def save(self) -> User:
        """Добавляет нового пользователя в базу"""
        self.cleaned_data.pop('password_again')
        profile = Profile.objects.create(avatar_filename='ava.jpg')
        return User.objects.create_user(**self.cleaned_data, profile=profile)


class SettingsForm(forms.Form):
    """Класс, отвечающий за форму изменение настроек профиля"""
    email = forms.EmailField(widget=forms.EmailInput)
    first_name = forms.CharField()
    last_name = forms.CharField()
    avatar = forms.ImageField(widget=forms.FileInput, required=False)

    def initFields(self, user: User):
        """Заполняет поля текущими значениями"""
        self.fields['email'].initial = user.email
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        
    def save(self, user: User):
        """Сохраняет изменения"""
        if self.cleaned_data['avatar']:
            profile = Profile.objects.get(user=user)
            profile.avatar = self.cleaned_data['avatar']
            profile.save()

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class AskForm(forms.Form):
    """Класс, отвечающий за форму отправки вопроса"""
    title = forms.CharField(max_length=256)
    text = forms.CharField(max_length=4096, widget=forms.Textarea)
    tags = forms.CharField(max_length=128, help_text='Enter tags splited by spaces')

    def clean(self):
        """Валидирует форму"""
        tags = self.cleaned_data['tags'].split()
        for tag in tags:
            if len(tag) > TAG_MAX_LENGTH:
                self.add_error('tags', f'Each tag can`t be longer that {TAG_MAX_LENGTH} characters.')

    def save(self, user: User) -> Question:
        """Добавляет в базу новый вопрос, теги, связи вопрос-тег, изменяет счётчики"""
        question = Question.objects.create(
            title=self.cleaned_data['title'],
            text=self.cleaned_data['text'],
            profile=Profile.objects.get(user=user)
        )

        tag_names = self.cleaned_data['tags'].split()
        for tag_name in tag_names:
            same_tags = Tag.objects.filter(name=tag_name)
            if not same_tags.exists():
                tag = Tag.objects.create(
                    name=tag_name,
                    questions=1,
                )
            else:
                tag = same_tags[0]
                tag.questions += 1
                tag.save()

            Link_QuestionTag.objects.create(
                question=question,
                tag=tag
            )

        return question
    

class AnswerForm(forms.Form):
    """Класс, отвечающий за форму отправки ответа на вопрос"""
    text = forms.CharField(max_length=4096, widget=forms.Textarea)

    def save(self, user: User, question: Question) -> Answer:
        "Добавляет в базу новый ответ на конкретный вопрос, изменяет счётчик ответов у вопроса"
        question.answers += 1
        question.save()

        return Answer.objects.create(
            text=self.cleaned_data['text'],
            profile=Profile.objects.get(user=user),
            question=question
        )