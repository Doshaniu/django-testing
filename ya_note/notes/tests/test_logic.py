from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreate(TestCase):

    NOTE_TEXT = 'Какой то текст'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных."""
        cls.user = User.objects.create(username='Username Username')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Новый текст',
            'slug': 'novaya-zametka'

        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        notes_before = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_after = Note.objects.count()
        self.assertEqual(notes_before, notes_after)

    def test_auth_user_create_note(self):
        """Зарегистрированый пользователь может создать заметку"""
        response = self.auth_client.post(self.url, data=self.form_data)

        success_url = reverse('notes:success')
        self.assertRedirects(response, success_url)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.slug, self.form_data['slug'])


class TestNotesEditDelete(TestCase):

    NOTE_TEXT = 'Какой то текст'
    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных."""
        cls.author = User.objects.create(username='Username Username')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.user = User.objects.create(username='Другой Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title='Заметка',
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='zametka'
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'zametka'}

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        response = self.author_client.post(self.delete_url)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_another_user_cant_delete_note_of_another_author(self):
        """Другой пользователь не может удалить чужую заметку."""
        response = self.user_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        response = self.author_client.post(
            self.edit_url, self.form_data
        )
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.user_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_slug_must_be_unique(self):
        """Слаг должен быть уникальным в пределах одного пользователя."""
        response = self.author_client.post(self.add_url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=(self.form_data['slug'] + WARNING)
        )
        self.assertEqual(form.data['title'], self.form_data['title'])
        self.assertEqual(form.data['slug'], self.form_data['slug'])


class TestNotesSlugGenerate(TestCase):
    NOTE_TEXT = 'Какой то текст'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных."""
        cls.author = User.objects.create(username='Username Username')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'Новая заметка без слага',
            'text': cls.NOTE_TEXT,
        }

    def test_slug_is_generated_automatically(self):
        """Автоматическая генерация слага из заголовка."""
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)
