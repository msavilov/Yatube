from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_correct_template_guest_client(self):
        """
        URL-адрес использует соответствующий шаблон для неавторизированного
        пользователя в users
        """
        templates_pages_names = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/logged_out.html': reverse('users:logout'),
            'users/password_reset_form.html':
                reverse('users:password_reset_form'),
            'users/password_reset_complete.html':
                reverse('users:password_reset_complete'),
            'users/password_reset_done.html':
                reverse('users:password_reset_done'),
            # 'users/password_reset_confirm.html':
            #     reverse('users:password_reset_confirm'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_correct_template_authorized_client(self):
        """
        URL-адрес использует соответствующий шаблон для неавторизированного
        пользователя в users
        """
        templates_pages_names = {
            'users/password_change_form.html':
                reverse('users:password_change'),
            'users/password_change_done.html':
                reverse('users:password_change_done'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_singup_show_correct_context(self):
        """Тест, что шаблон singup сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
