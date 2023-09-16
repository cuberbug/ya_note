"""
1. Главная страница
    + доступна анонимному пользователю.
2. Аутентифицированному пользователю доступна
    + страница со списком заметок notes/,
    + страница успешного добавления заметки done/,
    + страница добавления новой заметки add/.
3. Страницы
    + отдельной заметки,
    + удаления и редактирования заметки
        доступны только автору заметки.
        Если на эти страницы попытается зайти другой
        пользователь — вернётся ошибка 404.
4. При попытке перейти на страницу списка заметок,
    + страницу успешного добавления записи,
    + страницу добавления заметки,
    + отдельной заметки,
    + редактирования или удаления заметки
        анонимный пользователь перенаправляется на страницу логина.
5. Страницы
    + регистрации пользователей,
    + входа в учётную запись и выхода из неё
        доступны всем пользователям.
"""
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
def test_home_availability_for_anonymous_user(client, name):
    """
    Тест доступности страниц для анонима:
    * главная;
    * логин;
    * логаут;
    * регистрация.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    print(f'Аноним - запрос к url:{url} >>> {response.status_code}')


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(admin_client, name):
    """
    Тест доступности страниц для авторизованного пользователя:
    * список заметок;
    * добавление заметки;
    * успешное добавление заметки.
    """
    url = reverse(name)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK

    print(f'Юзер - запрос к url:{url} >>> {response.status_code}')


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
    ),
)
# В параметры теста добавляем имена parametrized_client и expected_status.
def test_pages_availability_for_different_users(
        parametrized_client, name, args, expected_status
):
    """
    Автору доступна страница: (а юзеру - нет)
    * со списком заметок;
    * успешного добавления заметки;
    * добавления новой заметки.
    """
    url = reverse(name, args=args)
    # Делаем запрос от имени клиента parametrized_client:
    response = parametrized_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == expected_status

    print(f'url:...{url} >>> {response.status_code}')


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args):
    """Тест редиректов анонима."""
    login_url = reverse('users:login')
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

    print(f'url:...{url} >>> {response.status_code} >>> {expected_url}')
