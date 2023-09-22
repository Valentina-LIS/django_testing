from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

URL_NOTES_SUCCESS = reverse('notes:success')


class TestNoteCreateEditDelete(TestCase):
    BASE_TITLE = 'Заголовок'
    NEW_TITLE = 'Новый заголовок'
    BASE_TEXT = 'Текст комментария'
    NEW_TEXT = 'Новый текст комментария'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.BASE_TITLE,
            text=cls.BASE_TEXT,
            author=cls.author
        )

        cls.success_url = URL_NOTES_SUCCESS
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.add_url = reverse('notes:add')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': 'form-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note(self):
        response = self.reader_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.get(slug=self.form_data['slug']).last()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.reader)

    def test_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.reader_client.post(
            self.add_url, data=self.form_data
        )
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        del self.form_data['slug']
        expected_slug = slugify(self.form_data['title'])
        response = self.reader_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.last()
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_reader_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.BASE_TEXT)
        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
