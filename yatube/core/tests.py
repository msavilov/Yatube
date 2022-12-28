from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class ViewTestClass(TestCase):

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_error_page(self):
        page = '/nonexist-page/'
        template = 'core/404.html'
        users = (
            self.authorized_client,
            self.guest_client,
        )
        for user in users:
            response = user.get(page)
            error_template = f'Ошибка: {page} ожидал шаблон {template}'
            self.assertTemplateUsed(response, template, error_template)
