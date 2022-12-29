from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

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
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.index_url = ('/', 'posts/index.html')
        self.group_posts_url = (f'/group/{self.group.slug}/',
                                'posts/group_list.html')
        self.profile_url = (f'/profile/{self.user.username}/',
                            'posts/profile.html')
        self.post_url = (f'/posts/{self.post.id}/', 'posts/post_detail.html')
        self.create_post_url = ('/create/', 'posts/edit_post.html')
        self.edit_post_url = (f'/posts/{self.post.id}/edit/',
                              'posts/edit_post.html')
        self.follow_url = ('/follow/', 'posts/follow.html')
        self.redirect_url = '/auth/login/?next='

    def test_urls_guest_client(self) -> None:
        """Тест общедоступных страниц для неавторизованного пользователя"""
        pages = (
            self.index_url,
            self.group_posts_url,
            self.profile_url,
            self.post_url,
        )
        for page, _ in pages:
            with self.subTest(page=page):
                cache.clear()
                response = self.guest_client.get(page)
                error_name = f'Отсутствует доступ к странице {page}'
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_name,
                )

    def test_urls_authorized_client(self) -> None:
        """Тест страниц для авторизованного пользователя"""
        pages = (
            self.index_url,
            self.group_posts_url,
            self.profile_url,
            self.post_url,
            self.create_post_url,
            self.edit_post_url,
            self.follow_url,
        )
        for page, _ in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                error_name = f'Отсутствует доступ к странице {page}'
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_name,
                )

    def test_urls_redirect_guest_client(self) -> None:
        """Тест переадрессаций для неавторизованного пользователя"""
        pages = (
            (self.create_post_url[0],
                f'{self.redirect_url}{self.create_post_url[0]}'),
            (self.edit_post_url[0],
                f'{self.redirect_url}{self.edit_post_url[0]}'),
        )
        for address, template in pages:
            with self.subTest(address=address):
                cache.clear()
                response = self.guest_client.get(address)
                self.assertRedirects(response, template)

    def test_urls_uses_correct_template_guest_client(self) -> None:
        """Тест ожидаемых шаблонов для неавторизованного пользователя"""
        pages = (
            self.index_url,
            self.group_posts_url,
            self.profile_url,
            self.post_url,
        )
        for address, template in pages:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                error_name = f'Ошибка: {address} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_urls_uses_correct_template_authorized_client(self) -> None:
        """Тест ожидаемых шаблонов для авторизованного пользователя"""
        pages = (
            self.index_url,
            self.group_posts_url,
            self.profile_url,
            self.post_url,
            self.create_post_url,
            self.edit_post_url,
            self.follow_url,
        )
        for address, template in pages:
            with self.subTest(address=address):
                cache.clear()
                response = self.authorized_client.get(address)
                error_name = f'Ошибка: {address} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_unexisting_page(self) -> None:
        """Тест доступа к несуществующей странице"""
        page = '/unexisting_page/'
        users = (
            self.authorized_client,
            self.guest_client,
        )
        for user in users:
            response = user.get(page)
            error_name = f'Доступ к несуществующей странице {page} для {user}'
            self.assertEqual(
                response.status_code,
                HTTPStatus.NOT_FOUND,
                error_name,
            )

    def test_url_uncorrect_user(self) -> None:
        """Тест доступа неавтора к редактированию поста"""
        page = self.edit_post_url[0]
        uncorrect_user = Client()
        response = uncorrect_user.post(
            page,
            {'username': 'uncorrect', 'password': 'user'})
        error_name = f'Неавтор не должен иметь доступ к редактированию {page}'
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            error_name,
        )

    def test_urls_redirect_uncorrect_user(self) -> None:
        """Тест переадрессации неавтора поста"""
        uncorrect_user = Client()
        response = uncorrect_user.post(
            self.edit_post_url[0],
            {'username': 'uncorrect', 'password': 'user'},
        )
        self.assertRedirects(response,
                             f'{self.redirect_url}{self.edit_post_url[0]}')
