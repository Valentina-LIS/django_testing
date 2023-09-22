from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

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
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст комментария',
            author=cls.author,
        )

    def test_note_order(self):
        url = reverse('notes:list')
        response = self.client.get(url)
        notes = response.context.get('object_list')
        self.assertIn(self.note, notes)

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
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_not_in_list_of_another_user(self):
        url = reverse('notes:list')
        response = self.reader_client.get(url)
        self.assertNotIn(self.note, response.context['object_list'])
