from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized_client(self):
        '''Проверка возможности создания поста'''
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'author': self.user,
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.last()
        error_not_equal = 'Данные не совпадают'
        self.assertEqual(post.text, form_data['text'], error_not_equal)
        self.assertEqual(post.group, self.group, error_not_equal)
        self.assertEqual(post.author, form_data['author'],
                         error_not_equal)
        self.assertEqual(post.image.name, 'posts/small.gif',
                         error_not_equal)
        self.assertEqual(Post.objects.count(), 1, 'Поcт не добавлен БД')

    def test_can_edit_post_authorized_client(self):
        '''Проверка возможности редактирования поста'''
        new_post = Post.objects.create(
            text='Исходные текст',
            author=self.user,
            group=self.group)
        new_group = Group.objects.create(
            title='Новая группа',
            slug='test_slug2',
            description='Тестовое описание',
        )
        form_data = {'text': 'Новый текст',
                     'group': new_group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': new_post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.last()
        error_assert_equal = 'Данные не совпадают'
        self.assertEqual(post.text, form_data['text'], error_assert_equal)
        self.assertEqual(post.group.id, form_data['group'], error_assert_equal)
        self.assertEqual(post.author, new_post.author, error_assert_equal)
        self.assertNotEqual(new_post.text, form_data['text'],
                            'Пользователь не может изменить содержание поста')
        self.assertNotEqual(new_post.group, form_data['group'],
                            'Пользователь не может изменить группу поста')
        self.assertEqual(self.group.posts.count(), 0,
                         'Пост после смены группы остался в старой группе')

    def test_can_not_edit_post_non_author(self):
        '''Проверка запрета создания поста не авторизованному пользователю'''
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id,
                     'author': self.user}
        non_author = Client('non_author')
        response = non_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(), 1,
                            'Поcт добавлен в базу данных по ошибке')

    def test_can_not_create_comment_guest_client(self):
        '''
        Проверка запрета создания комментария неавторизованному пользователю
        '''
        new_post = Post.objects.create(
            text='Исходные текст',
            author=self.user,
            group=self.group)
        form_data = {'text': 'Новый комментарий',
                     'post': new_post.id,
                     'author': self.user}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': new_post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Comment.objects.count(), 1,
                            'Комментарий добавлен в БД по ошибке')

    def test_create_comment_authorized_client(self):
        '''Проверка возможности создания комментария'''
        new_post = Post.objects.create(
            text='Исходные текст',
            author=self.user)
        form_data = {'text': 'Новый комментарий',
                     'post': new_post.id,
                     'author': self.user}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': new_post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comment = Comment.objects.last()
        error_not_equal = 'Данные не совпадают'
        self.assertEqual(comment.post.id, form_data['post'], error_not_equal)
        self.assertEqual(comment.text, form_data['text'], error_not_equal)
        self.assertEqual(comment.author, form_data['author'],
                         error_not_equal)
        self.assertEqual(Comment.objects.count(), 1,
                         'Комментарий не добавлен БД')
