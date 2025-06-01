from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель заметки')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author)

    def test_pages_availability(self):
        """Тест доступности главной страницы, страницы заметок, авторизации."""
        self.client.force_login(self.author)
        urls = ('notes:home', 'users:login', 'users:logout', 'users:signup')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_homepage_avialabale_for_anon(self):
        """Тест доступности главной страницы, логина, регистрации."""
        urls = ('notes:home', 'users:login', 'users:signup')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability(self):
        """Тест доступности страниц.

        Редактирования, удаления, просмотра заметок, только для автора.
        """
        users_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:edit', (self.note.slug,))
        )
        for user, status in users_status:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user.username, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_common_pages_availablity(self):
        """Тест доступности страниц заметок авторизованному пользователю."""
        self.client.force_login(self.author)
        urls = (
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add')
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа для анонимного пользователя."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                if args:
                    url = reverse(name, args=args)
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
