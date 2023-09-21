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

        all_notes = [
            Note(
                title=f'Заголовок {index}',
                text='Текст',
                author=cls.author,
                slug=f'uniq_slug_{index}'
            )
            for index in range(2)
        ]
        Note.objects.bulk_create(all_notes)
        cls.note = Note.objects.get(id=1)

    def test_note_order(self):
        url = reverse('notes:list')
        Note.objects.create(title='Новый', text='Текст2', author=self.author)
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        self.assertLess(notes[0].id, notes[1].id)

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

    def test_note_not_in_list_of_another_user(self):
        url = reverse('notes:list')
        response = self.reader_client.get(url)
        self.assertNotIn(self.note, response.context['object_list'])
