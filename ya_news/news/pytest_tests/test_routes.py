from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

pytestmark = pytest.mark.django_db

HOME_URL = 'news:home'
DETAIL_URL = 'news:detail'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGN_UP_URL = 'users:signup'


@pytest.mark.parametrize(
    'name',
    (
        HOME_URL,
        DETAIL_URL,
        LOGIN_URL,
        LOGOUT_URL,
        SIGN_UP_URL,
    )
)
def test_pages_availability(client, name, news):
    """Тест доступности страниц анонимному пользователю."""
    if name == DETAIL_URL:
        url = reverse(name, args=(news.id,))
        response = client.get(url)
    else:
        url = reverse(name)
    if name == LOGOUT_URL:
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('client'), 'redirect'),
    ]
)
@pytest.mark.parametrize(
    'name',
    (EDIT_URL, DELETE_URL)
)
def test_availability_for_comment_edit_and_delete_and_redirect_anon_user(
    parametrized_client, name, comment, expected_status, redirect_to_login,
):
    """Тест доступности страниц редактирования и удаления только для автора.
    Редирект анонимного пользователя на страницу логина.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)

    if expected_status == 'redirect':
        expected_url = f'{redirect_to_login}?next={url}'
        assertRedirects(response, expected_url)
    else:
        assert response.status_code == expected_status
