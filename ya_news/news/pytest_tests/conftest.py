from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура создания автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура создания другого пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура логина автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикструа логина другого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура создания новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    """Фикстура создания комментария."""
    comment = Comment.objects.create(
        text='Текст комментария',
        news=news,
        author=author,
    )
    return comment


@pytest.fixture
def created_news():
    """Фикстура для создания новостей на 1 больше чем показывает пагинатор."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def created_comments(news, author):
    """Фикстура создания 10-ти комментариев."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def redirect_news_home():
    """Фикстура редиректа на домашнюю странницу."""
    return reverse('news:home')


@pytest.fixture
def redirect_news_detail(news):
    """Фикстура редиректа отдельного поста новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def redirect_to_comments(redirect_news_detail):
    """Фикстура редиректа на комментарии определенной новости."""
    return redirect_news_detail + '#comments'


@pytest.fixture
def redirect_comment_delete(comment):
    """Фикстура редиректа удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def redirect_comment_edit(comment):
    """Фикстура редиректа редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def redirect_to_login():
    """Фикстура редиректа на страницу логина."""
    return reverse('users:login')
