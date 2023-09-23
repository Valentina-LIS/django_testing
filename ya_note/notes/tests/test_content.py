from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
        )

    def test_note_order(self):
        users_notes = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        url = reverse('notes:list')
        for user, value in users_notes:
            with self.subTest(user=user, value=value):
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, value)

    def test_form_on_create_and_edit_page(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for page, args in urls:
            with self.subTest(page=page, args=args):
                url = reverse(page, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
