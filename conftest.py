import pytest

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    """Модель пользователя-автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    """Залогиненный в клиенте автор."""
    client.force_login(author)
    return client


@pytest.fixture
def note(author):
    """Модель заметки."""
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author,
    )
    return note


@pytest.fixture
def slug_for_args(note):
    """Slug для заметки."""
    return note.slug,


@pytest.fixture
def form_data():
    """Подготавливает словарь для запроса на изменение заметки."""
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug',
    }
