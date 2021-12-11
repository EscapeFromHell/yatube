from django.test import TestCase

from ..models import Group, Post, User

USER = 'User'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'
SLUG = 'Тестовый слаг'
TEXT = 'Тестовая группа'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_text = post.text[:15]
        group = PostModelTest.group
        expected_title = group.title
        self.assertEqual(expected_text, str(post.text))
        self.assertEqual(expected_title, str(group.title))
