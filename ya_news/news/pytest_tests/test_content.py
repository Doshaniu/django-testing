import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, created_news, redirect_news_home):
    """Тест что на главной странице не более 10 новостей."""
    response = client.get(redirect_news_home)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, created_news, redirect_news_home):
    """Тест сортировки новостей от свежых к старым."""
    response = client.get(redirect_news_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, created_comments, redirect_news_detail):
    """Тест сортировки комментариев от старых к новым."""
    response = client.get(redirect_news_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(
    client, created_comments, redirect_news_detail,
):
    """Тест у анонимного пользователя нет формы написания комментария."""
    response = client.get(redirect_news_detail)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(
    author_client, created_comments, redirect_news_detail
):
    """Тест у авторизованного пользователя есть форма написания комментария."""
    response = author_client.get(redirect_news_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
