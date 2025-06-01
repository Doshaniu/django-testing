from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        'news:home',
        'users:login',
        'users:logout',
        'users:signup',
    )
)
def test_pages_availability(client, name):
    """Тест доступности страниц анонимному пользователю."""
    url = reverse(name)
    if name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'args',
    [lf('return_news_id')]
)
def test_detail_page_availability(client, args):
    """Тест доступности страницы отдельной новости анонимному пользователю."""
    url = reverse('news:detail', args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
    ]
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, name, return_comment_id, expected_status
):
    """Тест доступности страниц редактирования и удаления только для автора."""
    url = reverse(name, args=return_comment_id)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lf('return_comment_id')),
        ('news:delete', lf('return_comment_id')),
    )
)
def test_redirect_for_anonymous_client(client, name, args, redirect_to_login):
    """Редирект анонимного пользователя для логина в систему."""
    url = reverse(name, args=args)
    expected_url = f'{redirect_to_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
