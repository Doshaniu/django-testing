from http import HTTPStatus

from django.contrib.auth import get_user_model

from .base_class import BaseClass

User = get_user_model()


class TestRoutes(BaseClass):

    def test_pages_availability(self):
        """Тест доступности страниц."""
        urls = (
            # Для авторизованного пользователя
            (self.another_user_client, self.LIST_URL, HTTPStatus.OK),
            (self.another_user_client, self.SUCCESS_URL, HTTPStatus.OK),
            (self.another_user_client, self.ADD_URL, HTTPStatus.OK),

            # Для автора
            (self.another_user_client, self.DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.another_user_client, self.DELETE_URL, HTTPStatus.NOT_FOUND),
            (self.another_user_client, self.EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.author_client, self.DETAIL_URL, HTTPStatus.OK),
            (self.author_client, self.DELETE_URL, HTTPStatus.OK),
            (self.author_client, self.EDIT_URL, HTTPStatus.OK),

            # Общие страницы
            (self.client, self.LOGIN_URL, HTTPStatus.OK),
            (self.client, self.SIGN_UP_URL, HTTPStatus.OK),
            (self.client, self.HOME_URL, HTTPStatus.OK),
            (self.client, self.LOGOUT_URL, HTTPStatus.OK),

            # Редиректы
            (self.client, self.SUCCESS_URL, HTTPStatus.FOUND),
            (self.client, self.ADD_URL, HTTPStatus.FOUND),
            (self.client, self.LIST_URL, HTTPStatus.FOUND),
            (self.client, self.DELETE_URL, HTTPStatus.FOUND),
            (self.client, self.DETAIL_URL, HTTPStatus.FOUND),
            (self.client, self.EDIT_URL, HTTPStatus.FOUND),

        )
        for client, url, expected_status in urls:
            with self.subTest(
                client=client,
                url=url,
                expected_status=expected_status
            ):
                if url == self.LOGOUT_URL:
                    response = client.post(url)
                else:
                    response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа для анонимного пользователя."""
        urls = (
            (self.LIST_URL),
            (self.SUCCESS_URL),
            (self.ADD_URL),
            (self.DETAIL_URL),
            (self.DELETE_URL),
            (self.EDIT_URL),
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
