import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User, Follow

USER = 'User'
TITLE = 'Test_title'
DESCRIPTION = 'Test_descrip'
SLUG = 'test-slug'
TEXT = 'Тестовый текст'
COMMENT = 'Комментарий'

INDEX = '/'
GROUP_LIST = f'/group/{SLUG}/'
PROFILE = f'/profile/{USER}/'
POST_CREATE = '/create/'
FOLLOW = '/follow/'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif',
)


class PostPagesTests(TestCase):
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
            pk=1
        )

    def setUp(self):
        self.user = User.objects.get(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(author=self.user)
        self.POST_DETAIL = f'/posts/{self.post.id}/'
        self.POST_EDIT = f'/posts/{self.post.id}/edit/'

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': INDEX,
            'posts/group_list.html': GROUP_LIST,
            'posts/profile.html': PROFILE,
            'posts/post_detail.html': self.POST_DETAIL,
            'posts/create_post.html': POST_CREATE,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_author(self):
        if self.authorized_client == Post.author:
            response = self.authorized_client.get(self.POST_EDIT)
            self.assertTemplateUsed(response, 'posts/create_post.html')


class PostContextTests(TestCase):
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
        Group.objects.create(
            title='Title_test',
            description='Я усталь :(',
            slug='group-test'
        )
        cls.posts = []
        for id in range(13):
            cls.post = Post.objects.create(
                id=id,
                text=TEXT,
                author=User.objects.get(username=USER),
                group=Group.objects.get(title=TITLE),
                image=UPLOADED,
            )
            cls.posts.append(cls.post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.get(username=USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.get(title=TITLE)
        self.post = Post.objects.get(id=1)
        self.POST_DETAIL = f'/posts/{self.post.id}/'
        self.POST_EDIT = f'/posts/{self.post.id}/edit/'

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = self.post
        response_post = response.context['page_obj'][0]
        post_author = response_post.author
        post.group = response_post.group
        post_text = response_post.text
        post_image = response_post.image
        self.assertTrue(post_image)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post_text, post.text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_LIST)
        post = self.post
        response_post = response.context['page_obj'][0]
        post_author = response_post.author
        post.group = response_post.group
        post_text = response_post.text
        post_image = response_post.image
        self.assertTrue(post_image)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post_text, post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE)
        post = self.post
        response_post = response.context['page_obj'][0]
        post_author = response_post.author
        post.group = response_post.group
        post_text = response_post.text
        post_image = response_post.image
        self.assertTrue(post_image)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post_text, post.text)

    def test_first_group_list_page_contains_ten_records(self):
        index_response = self.client.get(INDEX)
        index_count = len(index_response.context['page_obj'])
        group_list_response = self.client.get(GROUP_LIST)
        group_list_count = len(group_list_response.context['page_obj'])
        profile_response = self.client.get(PROFILE)
        profile_count = len(profile_response.context['page_obj'])

        count_pages = [
            index_count,
            group_list_count,
            profile_count
        ]
        for count_page in count_pages:
            with self.subTest(count_page=count_page):
                self.assertEqual(count_page, 10)

    def test_second_group_list_page_contains_three_records(self):
        index_response = self.client.get(INDEX + '?page=2')
        index_count = len(index_response.context['page_obj'])
        group_list_response = self.client.get(GROUP_LIST + '?page=2')
        group_list_count = len(group_list_response.context['page_obj'])
        profile_response = self.client.get(PROFILE + '?page=2')
        profile_count = len(profile_response.context['page_obj'])

        count_pages = [
            index_count,
            group_list_count,
            profile_count
        ]
        for count_page in count_pages:
            with self.subTest(count_page=count_page):
                self.assertEqual(count_page, 3)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL)
        post = self.post
        response_post = response.context['post']
        post_author = response_post.author
        post_group = response_post.group
        post_text = response_post.text
        post_image = response_post.image
        self.assertTrue(post_image)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_text, post.text)

    def test_create_post_page_show_correct_context(self):
        """Форма редактирования поста."""
        if self.authorized_client == Post.author:
            response = self.authorized_client.get(self.POST_EDIT)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }

            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_create_post_form_correct_context(self):
        """Форма создания поста."""
        response = self.authorized_client.get(POST_CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_with_group_on_main(self):
        response = self.authorized_client.get(INDEX)
        post = self.post
        response_post = response.context['page_obj'][0]
        post_text = response_post.text
        self.assertEqual(post_text, post.text)

    def test_new_post_with_group_on_group_list(self):
        response = self.authorized_client.get(GROUP_LIST)
        post = self.post
        response_post = response.context['page_obj'][0]
        post_text = response_post.text
        group = response.context.get('group')
        self.assertEqual(post_text, post.text)
        self.assertEqual(group, self.group)

    def test_new_post_with_group_on_profile(self):
        response = self.authorized_client.get(GROUP_LIST)
        post = self.post
        response_post = response.context['page_obj'][0]
        post_text = response_post.text
        post_author = response_post.author
        self.assertEqual(post_text, post.text)
        self.assertEqual(post_author, self.user)

    def test_new_post_with_group_not_on_group_list(self):
        response = self.authorized_client.get('/group/group-test/')
        post = self.post
        response_post = response.context['page_obj']
        group = response.context.get('group')
        self.assertNotIn(post, response_post)
        self.assertNotEqual(group, self.group)


class CommentCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username=USER
        )
        Post.objects.create(
            author=User.objects.get(username=USER),
            text=TEXT,
            id=1
        )
        Comment.objects.create(
            post=Post.objects.get(id=1),
            author=User.objects.get(username=USER),
            text=COMMENT,
        )

    def setUp(self):
        self.user = User.objects.get(username=USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(id=1)
        self.POST_DETAIL = f'/posts/{self.post.id}/'

    def test_comment_on_post_detail_page(self):
        response = self.authorized_client.get(self.POST_DETAIL)
        comment = Comment.objects.get(text=COMMENT)
        response_comment = response.context['comments'][0]
        comment_text = response_comment.text
        self.assertEqual(comment_text, comment.text)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username=USER
        )
        Post.objects.create(
            author=User.objects.get(username=USER),
            text=TEXT,
            pk=1
        )

    def setUp(self):
        self.user = User.objects.get(username=USER)
        self.guest_client = Client()
        self.post = Post.objects.get(text=TEXT)

    def test_cache_index_page(self):
        response = self.guest_client.get(INDEX)
        Post.objects.all().delete()
        self.assertNotContains(response, self.post)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username=USER
        )
        User.objects.create(
            username='User_2'
        )
        Post.objects.create(
            author=User.objects.get(username=USER),
            text=TEXT,
            pk=1
        )

    def setUp(self):
        self.user = User.objects.get(username='User_2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(text=TEXT)

    def test_follow_add_delete(self):
        author = User.objects.get(username=USER)
        add = Follow.objects.create(
            user=User.objects.get(username='User_2'),
            author=author,
        )
        delete = Follow.objects.filter(
            user=User.objects.get(username='User_2'),
            author=author,
        ).delete()
        self.assertNotEqual(add, delete)

    def test_follow_index(self):
        author = User.objects.get(username=USER)
        Follow.objects.create(
            user=User.objects.get(username='User_2'),
            author=author,
        )
        response = self.authorized_client.get(FOLLOW)
        post = self.post
        response_post = response.context['page_obj'][0]
        post_text = response_post.text
        self.assertEqual(post_text, post.text)
        Follow.objects.filter(
            user=User.objects.get(username='User_2'),
            author=author,
        ).delete()
        response = self.authorized_client.get(FOLLOW)
        post = self.post
        self.assertNotContains(response, post)
