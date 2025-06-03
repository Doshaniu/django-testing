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
        notes_before = Note.objects.filter(author=self.author).count()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)

        self.assertRedirects(response, self.SUCCESS_URL)

        notes_count = Note.objects.filter(author=self.author).count()
        self.assertEqual(notes_count, notes_before + 1)

        note = Note.objects.latest('id')
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
        old_text = self.note.text
        old_slug = self.note.slug
        """Другой пользователь не может удалить чужую заметку."""
        response = self.another_user_client.post(
            self.DELETE_URL,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_count = Note.objects.filter(author=self.author).count()
        self.assertEqual(note_count, 1)
        self.assertEqual(self.note.text, old_text)
        self.assertEqual(self.note.slug, old_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        old_author = self.note.author
        response = self.author_client.post(
            self.EDIT_URL, self.form_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, old_author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        old_text = self.note.text
        old_slug = self.note.slug
        response = self.another_user_client.post(
            self.EDIT_URL, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, old_text)
        self.assertEqual(self.note.slug, old_slug)

    def test_slug_must_be_unique(self):
        """Слаг должен быть уникальным в пределах одного пользователя."""
        self.existing_slug_note = Note.objects.create(
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
        response = self.author_client.post(
            self.ADD_URL, data=self.form_data_without_slug)
        self.assertRedirects(response, self.SUCCESS_URL)

        note = Note.objects.get(title=self.form_data_without_slug['title'])

        expected_slug = slugify(self.form_data_without_slug['title'])
        self.assertEqual(note.slug, expected_slug)
