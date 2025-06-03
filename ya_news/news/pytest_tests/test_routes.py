from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    (
        'news:home',
        'users:login',
        'users:logout',
        'users:signup',
        'news:detail',
    )
)
def test_pages_availability(client, name, news):
    """Тест доступности страниц анонимному пользователю."""
    if name == 'news:detail':
        url = reverse(name, args=(news.id,))
        response = client.get(url)
    else:
        url = reverse(name)
    if name == 'users:logout':
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
    ('news:edit', 'news:delete')
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
