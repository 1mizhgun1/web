from django.core.management.base import BaseCommand
from front.services import cache_popular_tags


class Command(BaseCommand):
    help = 'Кэширует популярные тэги'

    def handle(self, *args, **kwargs):
        print('IT WORKS')
        cache_popular_tags()