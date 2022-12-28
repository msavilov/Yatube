from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.password = 'G45$Ty231'

    def test_create_post(self):
        '''Проверка возможности создания пользователя'''
        users_count = User.objects.count()
        form_data = {
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password}
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:index'))
        error_name1 = 'Данные пользователей не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(User.objects.filter(
            username=self.username,
            email=self.email).exists(), error_name1)
        error_name2 = 'Пользователь не добавлен в базу данных'
        self.assertEqual(User.objects.count(), users_count + 1, error_name2)
