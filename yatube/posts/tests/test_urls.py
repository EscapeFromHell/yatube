from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User

USER = 'User'
TITLE = 'Test_title'
DESCRIPTION = 'Test_descrip'
SLUG = 'test-slug'
TEXT = 'Тестовый текст'

INDEX = '/'
GROUP_LIST = f'/group/{SLUG}/'
PROFILE = f'/profile/{USER}/'
POST_CREATE = '/create/'
UNEXISTING_PAGE = '/unexisting_page/'


class MainURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(INDEX)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class YatubeURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username=USER
        )
        Group.objects.create(
            title=TITLE,
            description=DESCRIPTION,
            slug=SLUG
        )
        Post.objects.create(
            author=User.objects.get(username=USER),
            text=TEXT,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username=USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(author=self.user)
        self.POST_DETAIL = f'/posts/{self.post.id}/'
        self.POST_EDIT = f'/posts/{self.post.id}/edit/'

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': INDEX,
            'posts/group_list.html': GROUP_LIST,
            'posts/profile.html': PROFILE,
            'posts/post_detail.html': self.POST_DETAIL
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_loggin(self):
        response = self.authorized_client.get(POST_CREATE)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_uses_correct_template_author(self):
        if self.authorized_client == Post.author:
            response = self.authorized_client.get(self.POST_EDIT)
            self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_uses_correct_unexisting_page(self):
        response = self.guest_client.get(UNEXISTING_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
