from http import HTTPStatus

from colorama import Fore
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


PRINT: bool = True


class TestNoteCreation(TestCase):
    """Тест создания заметки."""
    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
        }

        if PRINT:
            print('=============================================')
            print('\n>>> Tест создания заметки:\n')
            print('Подготовка данных для тестов:')
            print(f'\t>создан пользователь: {cls.author}')

    def test_anonymous_user_cant_create_note(self):
        """Тест создания заметки анонимным пользователем."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

        if PRINT and notes_count == 0:
            status = f'{Fore.GREEN} >> OK{Fore.RESET}'
            print(f'Тест создания заметки анонимным пользователем: {status}')

    def test_user_can_create_note(self):
        """Тест создания заметки авторизованным пользователем."""
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.author, self.author)

        if PRINT and (
            notes_count == 1
            and note.title == self.TITLE
            and note.text == self.TEXT
            and note.author == self.author
        ):
            status = f'{Fore.GREEN} >> OK{Fore.RESET}'
            print(
                'Тест создания заметки авторизованным пользователем: '
                f'{status}'
            )


class TestNoteEditDelete(TestCase):
    """Тест редактирования и удаления заметок."""
    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст заметки'

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Юзер')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
        }

        if PRINT:
            print('=============================================')
            print('\n>>> Тест редактирования и удаления заметок:\n')
            print('Подготовка данных для тестов:')
            print(f'\t>созданы пользователи: {cls.author}, {cls.reader}')
            print(f'\t>создана тестовая заметка: {cls.note.slug}')

    def test_author_can_delete_comment(self):
        """Тест удаления заметки автором."""
        self.author_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

        if PRINT and notes_count == 0:
            status = f'{Fore.GREEN} >> OK{Fore.RESET}'
            print(f'Тест удаления заметки её автором: {status}')

    def test_user_cant_delete_note_of_another_user(self):
        """Тест удаления заметки другим пользователем."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        if PRINT and (
            notes_count == 1 and response.status_code == HTTPStatus.NOT_FOUND
        ):
            status = f'{Fore.GREEN} >> OK{Fore.RESET}'
            print(f'Тест удаления заметки другим пользователем: {status}')

    def test_author_can_edit_comment(self):
        """Тест редактирования заметки автором."""
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)

        if PRINT and (
            self.note.title == self.NEW_TITLE
            and self.note.text == self.NEW_TEXT
        ):
            status = f'{Fore.GREEN} >> OK{Fore.RESET}'
            print(f'Тест редактирования заметки её автором: {status}')

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест редактирования заметки другим пользователем."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)

        if PRINT and (
            self.note.title == self.TITLE
            and self.note.text == self.TEXT
            and response.status_code == HTTPStatus.NOT_FOUND
        ):
            status = f'{Fore.GREEN} >> OK{Fore.RESET}'
            print(
                f'Тест редактирования заметки другим пользователем: {status}'
            )
