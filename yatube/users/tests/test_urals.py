from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='test_name',
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_guest_client(self) -> None:
        """Тест общедоступных страниц для неавторизованного пользователя"""
        pages = {
            '/auth/signup/',
            '/auth/login/',
            '/auth/logout/',
            '/auth/password_reset_form/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
            # '/reset/<uidb64>/<token>/'
        }
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                error_name = f'Отсутствует доступ к странице {page}'
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_name,
                )

    def test_users_urls_authorized_client(self) -> None:
        """Тест страниц для авторизованного пользователя"""
        pages = {
            '/auth/password_change/',
            '/auth/password_change/done/',
        }
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                error_name = f'Отсутствует доступ к странице {page}'
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_name,
                )

    def test_users_urls_correct_template_guest_client(self) -> None:
        """Тест ожидаемых шаблонов для неавторизованного пользователя"""
        pages = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset_form/': 'users/password_reset_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            # '/reset/<uidb64>/<token>/': 'users/password_reset_confirm.html',
        }
        for address, template in pages.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                error_name = f'Ошибка: {address} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_uses_urls_correct_template_authorized_client(self) -> None:
        """Тест ожидаемых шаблонов для авторизованного пользователя"""
        pages = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }
        for address, template in pages.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                error_name = f'Ошибка: {address} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_urls_redirect_guest_client(self) -> None:
        """Тест переадрессаций для неавторизованного пользователя"""
        pages = {
            '/auth/password_change/':
                '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
            '/auth/login/?next=/auth/password_change/done/',
        }
        for address, template in pages.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, template)
