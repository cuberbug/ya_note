# from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

"""
Здесь могла быть ваша реклама!

Страница со списком заметок:
    X записи отсортированы по pk в порядке возрастания
Подробная страница заметки:
    X Проверить видимость формы автором
"""


class TestNoteListPage(TestCase):
    """Тест контента страницы со списком заметок."""
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        print('\n>>> Tест контента.\n')
        print('Подготовка данных для тестов:')

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
        print(f'\t>создан пользователь: {cls.author}')
        print('=============================================')

    def test_news_order(self):
        """Тест сортировки заметок."""
        print('\nТест сортировки заметок:')
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_pk = [note.pk for note in object_list]
        sorted_pk = sorted(all_pk)
        print(f'\t{all_pk} == {sorted_pk}\n')
        self.assertEqual(all_pk, sorted_pk)

    def test_authorized_client_has_form(self):
        """Видит ли авторизованный юзер форму?"""
        print('\nВидит ли авторизованный юзер форму?')
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        if response.context['form']:
            print('\t - да, видит.')
        self.assertIn('form', response.context)
