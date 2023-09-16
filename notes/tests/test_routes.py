from http import HTTPStatus

from colorama import Fore
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


PRINT: bool = True


class TestRouters(TestCase):
    """Тест маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Юзер')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

        if PRINT:
            print('=============================================')
            print('\n>>> Тест маршрутов.\n')
            print('Подготовка данных для тестов:')
            print(f'\t>созданы пользователи: {cls.author}, {cls.reader}')
            print(f'\t>создана тестовая заметка: {cls.notes.slug}')

    def test_pages_availability(self):
        """Тест доступности страниц."""

        if PRINT:
            print('Тест доступности страниц:')

        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

                if PRINT:
                    status = f'{Fore.GREEN}{response.status_code}{Fore.RESET}'
                    print(f'\t{status} -> {url}')

    def test_availability_for_notes_edit_and_delete(self):
        """Тест юзера и автора на доступ к действиям с записями."""

        if PRINT:
            print('Тест юзера и автора на доступ к действиям с записями:')

        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete',):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

                    if PRINT:
                        print(
                            f'\t{user}: {Fore.GREEN}{response.status_code}'
                            f'{Fore.RESET} -> {url}'
                        )

    def test_redirect_for_anonymous_client(self):
        """Тест переадресации анонима с недоступных страниц."""

        if PRINT:
            print('Тест переадресации анонима с недоступных страниц:')

        urls_edit = (
            ('notes:list', None),
            ('notes:detail', (self.notes.slug,)),
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
            # ('notes:success', None),
        )
        login_url = reverse('users:login')
        for name, args in urls_edit:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

                if PRINT:
                    status = f'{Fore.GREEN}{response.status_code}{Fore.RESET}'
                    print(f'\t{status} -> {redirect_url}')
