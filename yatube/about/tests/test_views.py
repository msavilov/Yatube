from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AboutViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_static_page_guest_client(self) -> None:
        """Проверяем доступность страницы по URL"""
        pages = ('/about/author/', '/about/tech/')
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                error_name = f'Отсутствует доступ к странице {page}'
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_name,
                )

    def test_urls_uses_correct_template(self) -> None:
        """Проверяем корректность вызова шаблона используемого URL-адрес"""
        pages = (
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
        )
        for adress, template in pages:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                error_name = (f'Шаблон по адресу {adress} не соответствует '
                              + f'ожидаемому шаблону {template}.')
                self.assertTemplateUsed(response, template, error_name)

    def test_correct_template_authorized_client(self):
        """
        URL-адрес использует соответствующий шаблон для авторизированного
        пользователя  в about
        """
        templates_pages_names = (
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech')),
        )
        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_template_guest_client(self):
        """
        URL-адрес использует соответствующий шаблон для авторизированного
        пользователя в about
        """
        templates_pages_names = (
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech')),
        )
        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
