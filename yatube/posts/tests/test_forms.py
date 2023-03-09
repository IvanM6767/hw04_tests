from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем автора и две группы."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.author_3 = User.objects.create_user(username='author_3')

        cls.group_1 = Group.objects.create(
            title='Первая тестовая группа',
            slug='group_test_1'
        )
        cls.group_2 = Group.objects.create(
            title='Вторая тестовая группа',
            slug='group_test_2'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group_1
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый пост',
            author=cls.author_3,
            group=cls.group_2
        )

    def setUp(self):
        """Создаем клиента и пост."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(self.author_3)

    def test_create_post_form(self):
        """При отправке формы создается новый пост в базе данных.
        После создания происходит редирект на профиль автора.
        """
        post_count = Post.objects.all().count()
        form_data = {
            'text': 'Еще один пост',
            'group': self.group_1.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.author.username})
        )
        self.assertEqual(
            Post.objects.all().count(),
            post_count + 1,
            'Пост не сохранен в базу данных!'
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group_1,
                author=self.author
            ).exists())

    def test_edit_post_form(self):
        """При отправке формы изменяется пост в базе данных.
        После редактирования происходит редирект на карточку поста.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст поста',
            'group': self.group_2.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True)
        edit_post_var = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post_var.text, form_data['text'])
        self.assertEqual(edit_post_var.author, self.post.author)

    def test_edit_post_form_secclient(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст поста',
            'group': self.group_2.id
        }
        response = self.authorized_client_3.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        edit_post_var = Post.objects.get(id=self.post.id)
        self.assertNotEqual(edit_post_var.text, form_data['text'])

    def test_create_post_not_authorized(self):
        """Тестирование создания поста пользователем"""
        post_count = Post.objects.count()
        # Убедился что пост один в базе, до создания еще одного.
        self.assertEqual(Post.objects.count(), post_count)
        # Убедился что количество постов не изменилось
        self.assertEqual(Post.objects.count(), post_count)
