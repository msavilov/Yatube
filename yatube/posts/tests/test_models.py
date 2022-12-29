from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import PREVIEW_LEN, Comment, Group, Post

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
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_models = (
            (self.post.text[:PREVIEW_LEN], str(self.post)),
            (self.group.title, str(self.group)),
            (self.comment.text, str(self.comment)),
        )
        for value, expected in test_models:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_verbose_name_post(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = (
            ('text', 'Текст поста'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа'),
            ('image', 'Картинка'),
        )
        for value, expected in field_verboses:
            with self.subTest(value=value):
                error = f'Поле {value} ожидало значение {expected}'
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected, error)

    def test_help_text_post(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = (
            ('text', 'Введите текст поста'),
            ('group', 'Выберите группу'),
        )
        for value, expected in field_help_texts:
            with self.subTest(value=value):
                error = f'Поле {value} ожидало значение {expected}'
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected, error)

    def test_verbose_name_comment(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = (
            ('text', 'Добавить комментарий'),
        )
        for value, expected in field_verboses:
            with self.subTest(value=value):
                error = f'Поле {value} ожидало значение {expected}'
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name,
                    expected, error)

    def test_help_text_comment(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_help_texts = (
            ('text', 'Текст нового комментария'),
        )
        for value, expected in field_help_texts:
            with self.subTest(value=value):
                error = f'Поле {value} ожидало значение {expected}'
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected, error)
