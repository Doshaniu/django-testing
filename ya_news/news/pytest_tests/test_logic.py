from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, redirect_news_detail, form_data, redirect_to_login
):
    """Тест анонимный пользователь не может отправить комментарий."""
    response = client.post(redirect_news_detail, data=form_data)
    expected_url = f'{redirect_to_login}?next={redirect_news_detail}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, redirect_news_detail, form_data, news, author
):
    """Тест авторизованный пользователь может отправить комментарий."""
    response = author_client.post(redirect_news_detail, data=form_data)
    assertRedirects(response, f'{redirect_news_detail}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, redirect_news_detail):
    """Тест фильтр запрещенных слов"""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(redirect_news_detail, data=bad_words_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, redirect_to_comments, redirect_comment_delete
):
    """Тест автор может удалить комментарий."""
    response = author_client.post(redirect_comment_delete)
    assertRedirects(response, redirect_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, redirect_comment_delete
):
    """Тест пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(redirect_comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client,
        redirect_comment_edit,
        form_data,
        redirect_to_comments,
        comment,
        author,
        news
):
    """Тест автор может редактировать свой комментарий."""
    response = author_client.post(redirect_comment_edit, data=form_data)
    assertRedirects(response, redirect_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        redirect_comment_edit,
        comment,
        form_data
):
    """Тест пользователь не может редактировать чужой комментарий."""
    original_text = comment.text
    response = not_author_client.post(redirect_comment_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
