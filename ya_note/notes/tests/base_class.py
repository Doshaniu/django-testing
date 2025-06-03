from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class BaseClass(TestCase):

    HOME_URL = reverse('notes:home')
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')

    NOTES_SLUG = 'note-slug'

    EDIT_URL = reverse('notes:edit', args=(NOTES_SLUG,))
    DELETE_URL = reverse('notes:delete', args=(NOTES_SLUG,))
    DETAIL_URL = reverse('notes:detail', args=(NOTES_SLUG,))

    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGN_UP_URL = reverse('users:signup')

    NOTE_TEXT = 'Какой то текст'
    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заметка',
            author=cls.author,
            text=cls.NOTE_TEXT,
            slug=cls.NOTES_SLUG,
        )
        cls.another_user = User.objects.create(username='Другой автор')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.another_note = Note.objects.create(
            title='Заметка другого автора',
            author=cls.another_user,
            text='Другой текст',
        )
        cls.form_data = {
            'title': 'Новая заметка',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'novaya-zametka'
        }
        cls.form_data_without_slug = {
            'title': 'Заголовок',
            'text': cls.NOTE_TEXT
        }
