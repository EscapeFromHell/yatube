import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Post, User

USER = 'User'
TEXT = 'Тестовый текст'
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


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username=USER
        )
        Post.objects.create(
            author=User.objects.get(username=USER),
            text=TEXT,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.get(username=USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'image': UPLOADED,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        posts_count = Post.objects.count()
        not_edit_post = Post.objects.get(text=TEXT)
        form_data = {
            'text': 'Редакция поста',
        }
        post = Post.objects.get(text=TEXT)
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        edit_post = Post.objects.get(id=post.id)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(edit_post.text, not_edit_post.text)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username=USER
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

    def test_create_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        post = Post.objects.get(text=TEXT)
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment_guest(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        post = Post.objects.get(text=TEXT)
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
