from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

TEST_OF_POST = 13

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='test_name',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            id=1,
            text='Тестовое описание поста',
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=(
                    b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B'),
                content_type='image/gif',
            ),
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.index_url = (reverse('posts:index'), 'posts/index.html')
        self.group_list_url = (reverse('posts:group_list',
                               kwargs={'slug': f'{self.group.slug}'}),
                               'posts/group_list.html')
        self.profile_url = (reverse('posts:profile',
                            kwargs={'username': f'{self.user.username}'}),
                            'posts/profile.html')
        self.post_detail = (reverse('posts:post_detail',
                            kwargs={'post_id': f'{self.post.id}'}),
                            'posts/post_detail.html')
        self.create_post_url = (reverse('posts:post_create'),
                                'posts/edit_post.html')
        self.post_edit_url = (reverse('posts:post_edit',
                              kwargs={'post_id': f'{self.post.id}'}),
                              'posts/edit_post.html')

    def test_pages_uses_correct_template_authorized_client(self):
        """
        URL-адрес использует соответствующий шаблон для авторизированного
        пользователя
        """
        templates_pages_names = (
            self.index_url,
            self.group_list_url,
            self.profile_url,
            self.post_detail,
            self.create_post_url,
            self.post_edit_url,
        )
        for reverse_name, template in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_guest_client(self):
        """
        Тест, что URL-адрес использует соответствующий шаблон для
        неавторизированного пользователя
        """
        templates_pages_names = (
            self.index_url,
            self.group_list_url,
            self.profile_url,
            self.post_detail,
        )
        for reverse_name, template in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Тест, что шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.image, self.post.image)

    def test_list_page_show_correct_context(self):
        """Тест, что шаблон group_list сформирован с правильным контекстом."""
        pages = (
            self.group_list_url,
            self.profile_url,
        )
        for reverse_name, _ in pages:
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.context['post'].text, self.post.text)
                self.assertEqual(
                    response.context['post'].group, self.post.group)
                self.assertEqual(
                    response.context['post'].author, self.post.author)
                self.assertEqual(
                    response.context['post'].image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Тест, что шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            self.post_detail[0])
        post_text_0 = {
            response.context['post'].text: self.post.text,
            response.context['post'].group: self.group,
            response.context['post'].author: self.post.author,
            response.context['post'].image: self.post.image}
        for value, expected in post_text_0.items():
            cache.clear()
            self.assertEqual(post_text_0[value], expected)

    def test_post_create_page_show_correct_context(self):
        """Тест, что шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.create_post_url[0])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                cache.clear()
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Тест, что шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_edit_url[0])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                cache.clear()
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Тест, что пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group,
            image=SimpleUploadedFile(
                name='test_gif_image.gif',
                content=(
                    b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B'),
                content_type='image/gif',
            ),
        )
        names = (
            ('index', self.index_url[0]),
            ('group_list', self.group_list_url[0]),
            ('profile', self.profile_url[0]),
        )
        for key, value in names:
            with self.subTest(value=value):
                cache.clear()
                response = self.authorized_client.get(value)
                name = response.context['page_obj']
                self.assertIn(post, name, f'поста нет на странице {key}')


class PaginatorViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        self.index_url = (reverse('posts:index'), 'posts/index.html')
        self.group_list_url = (reverse('posts:group_list',
                               kwargs={'slug': f'{self.group.slug}'}),
                               'posts/group_list.html')
        self.profile_url = (reverse('posts:profile',
                            kwargs={'username': f'{self.user.username}'}),
                            'posts/profile.html')
        list_posts: list = []
        for i in range(TEST_OF_POST):
            list_posts.append(Post(text=f'Тестовый текст {i}',
                                   group=self.group,
                                   author=self.user))
        Post.objects.bulk_create(list_posts)

    def test_correct_page_context_guest_client(self):
        '''Проверка количества постов на первой и второй страницах. '''
        pages = (
            self.index_url[0],
            self.group_list_url[0],
            self.profile_url[0],
        )
        for page in pages:
            with self.subTest(page=page):
                cache.clear()
                response1 = self.guest_client.get(page)
                response2 = self.guest_client.get(page + '?page=2')
                self.assertEqual(len(response1.context['page_obj']), 10)
                self.assertEqual(len(response2.context['page_obj']), 3)

    def test_correct_page_context_authorized_client(self):
        '''Проверка контекста страниц авторизованного пользователя'''
        pages = (
            self.index_url[0],
            self.group_list_url[0],
            self.profile_url[0],
        )
        for page in pages:
            with self.subTest(page=page):
                cache.clear()
                response1 = self.authorized_client.get(page)
                response2 = self.authorized_client.get(
                    page + '?page=2')
                self.assertEqual(len(response1.context['page_obj']), 10)
                self.assertEqual(len(response2.context['page_obj']), 3)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='test_name',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            id=1,
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_pages(self):
        """Тест кэширования страниц"""
        pages = (
            (reverse('posts:index')),
        )
        for page in pages:
            with self.subTest(page=page):
                post = Post.objects.create(
                    text='Тестовый текст',
                    author=self.user,
                    group=self.group)
                cache.clear()
                first_state = self.authorized_client.get(page)
                post.delete()
                second_state = self.authorized_client.get(page)
                self.assertEqual(first_state.content,
                                 second_state.content,
                                 ('До очистки кеша, пост существует'))
                cache.clear()
                third_state = self.authorized_client.get(page)
                self.assertNotEqual(first_state.content,
                                    third_state.content,
                                    ('После обновления кеша, пост должен '
                                     + 'отсутствовать'))


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='author',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            id=1,
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.authorized_client = Client()
        self.new_user = User.objects.create_user(username='following')
        self.authorized_client.force_login(self.new_user)

    def test_add_follow_authorized_client(self):
        """
        Проверка создания подписки на автора у авторизированного клиента
        """
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        cache.clear()
        self.assertEqual(Follow.objects.all().count(), 1,
                         'Подписка не была создана')

    def test_can_not_add_follow_guest_client(self):
        """
        Проверка невозможности создания подписки у неавторизированного клиента
        """
        self.guest_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        cache.clear()
        self.assertEqual(Follow.objects.all().count(), 0,
                         'Подписка не былжна была быть создана')

    def test_unfollow_authorized_client(self):
        """Проверка возможности отписаться от автора"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        cache.clear()
        self.assertEqual(Follow.objects.all().count(), 1,
                         'Подписка не была создана')
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username}))
        cache.clear()
        self.assertEqual(Follow.objects.all().count(), 0,
                         'Подписка не была удалена')

    def test_subscription_authorized_client(self):
        """Проверка, что новая запись появляется в подписках"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        cache.clear()
        response = self.authorized_client.get('/follow/')
        post_text = response.context['page_obj'][0].text
        self.assertEqual(post_text, self.post.text,
                         'Пост после подписки не появился в подписках')
