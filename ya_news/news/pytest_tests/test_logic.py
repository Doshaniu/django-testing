from http import HTTPStatus

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

FORM_DATA = {
    'text': 'Другой текст комментария'
}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
    client, redirect_news_detail, redirect_to_login
):
    """Тест анонимный пользователь не может отправить комментарий."""
    response = client.post(redirect_news_detail, data=FORM_DATA)
    expected_url = f'{redirect_to_login}?next={redirect_news_detail}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, redirect_news_detail, news, author
):
    """Тест авторизованный пользователь может отправить комментарий."""
    response = author_client.post(redirect_news_detail, data=FORM_DATA)
    assertRedirects(response, f'{redirect_news_detail}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
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
    not_author_client, redirect_comment_delete, comment, news
):
    """Тест пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(redirect_comment_delete)
    updated_comment = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert updated_comment.text == comment.text
    assert updated_comment.author_id == comment.author_id
    assert updated_comment.news_id == comment.news_id


def test_author_can_edit_comment(
        author_client,
        redirect_comment_edit,
        redirect_to_comments,
        comment
):
    """Тест автор может редактировать свой комментарий."""
    response = author_client.post(redirect_comment_edit, data=FORM_DATA)
    assertRedirects(response, redirect_to_comments)
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        redirect_comment_edit,
        comment,
):
    """Тест пользователь не может редактировать чужой комментарий."""
    response = not_author_client.post(redirect_comment_edit, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == comment.text
    assert updated_comment.author_id == comment.author_id
    assert updated_comment.news_id == comment.news_id
