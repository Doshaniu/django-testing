from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from .base_class import BaseClass


class TestNoteCreate(BaseClass):

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        notes_before = Note.objects.count()
        self.client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(notes_before, Note.objects.count())

    def test_auth_user_create_note(self):
        """Зарегистрированый пользователь может создать заметку"""
        Note.objects.all().delete()

        response = self.author_client.post(self.ADD_URL, data=self.form_data)

        self.assertRedirects(response, self.SUCCESS_URL)

        notes_count = Note.objects.filter(author=self.author).count()
        self.assertEqual(notes_count, 1)

        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        response = self.author_client.post(
            self.DELETE_URL
        )

        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        notes_count = Note.objects.filter(author=self.author).count()
        self.assertEqual(notes_count, 0)

    def test_another_user_cant_delete_note_of_another_author(self):
        """Другой пользователь не может удалить чужую заметку."""
        response = self.another_user_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_count = Note.objects.filter(author=self.author).count()
        self.assertEqual(note_count, 1)
        author_note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(author_note.text, self.NOTE_TEXT)
        self.assertEqual(author_note.slug, self.NOTES_SLUG)
        self.assertEqual(author_note.author, self.author)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        response = self.author_client.post(
            self.EDIT_URL, self.form_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)

        edited_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])
        self.assertEqual(edited_note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.another_user_client.post(
            self.EDIT_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        original_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(original_note.text, self.NOTE_TEXT)
        self.assertEqual(original_note.slug, self.NOTES_SLUG)
        self.assertEqual(original_note.author, self.author)

    def test_slug_must_be_unique(self):
        """Слаг должен быть уникальным в пределах одного пользователя."""
        Note.objects.create(
            title='Дубликат',
            author=self.author,
            text='Повтор slug',
            slug='novaya-zametka'
        )
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=(self.form_data['slug'] + WARNING)
        )
        self.assertEqual(form.data['title'], self.form_data['title'])
        self.assertEqual(form.data['slug'], self.form_data['slug'])

    def test_slug_is_generated_automatically(self):
        """Автоматическая генерация слага из заголовка."""
        Note.objects.all().delete()
        response = self.author_client.post(
            self.ADD_URL, data=self.form_data_without_slug)
        self.assertRedirects(response, self.SUCCESS_URL)

        note = Note.objects.get()

        expected_slug = slugify(self.form_data_without_slug['title'])
        self.assertEqual(note.slug, expected_slug)
