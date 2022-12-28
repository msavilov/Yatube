from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import PREVIEW_LEN, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста для проведения тестирования',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_models = {
            self.post.text[:PREVIEW_LEN]: str(self.post),
            self.group.title: str(self.group),
        }
        for value, expected in test_models.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                error = f'Поле {value} ожидало значение {expected}'
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected, error)

    def test_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                error = f'Поле {value} ожидало значение {expected}'
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected, error)
