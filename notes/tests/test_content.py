from colorama import Fore
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


PRINT: bool = True


class TestNoteListPage(TestCase):
    """Тест контента страницы со списком заметок."""
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Автор')
        Note.objects.bulk_create(
            Note(
                title=f'Заметка {slug}',
                text='Просто текст.',
                author=cls.author,
                slug=1+slug
            )
            for slug in range(2)
        )

        if PRINT:
            print('=============================================')
            print('\n>>> Tест контента.\n')
            print('Подготовка данных для тестов:')
            print(f'\t>создан пользователь: {cls.author}')

    def test_news_order(self):
        """Тест сортировки заметок."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_pk = [note.pk for note in object_list]
        sorted_pk = sorted(all_pk)
        self.assertEqual(all_pk, sorted_pk)

        if PRINT and all_pk == sorted_pk:
            status = f'{Fore.GREEN} >> OK{Fore.RESET}'
            print(f'\nТест сортировки заметок: {status}')

    def test_authorized_client_has_form(self):
        """Видит ли авторизованный юзер форму?"""
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        self.assertIn('form', response.context)

        if PRINT and response.context['form']:
            status = f'{Fore.GREEN} - да, видит.{Fore.RESET}'
            print(f'\nВидит ли авторизованный юзер форму? {status}')
