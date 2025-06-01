from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых заметок и пользователя."""
        cls.author = User.objects.create_user(username='Автор')
        cls.note = Note.objects.create(
            title='Заметка',
            author=cls.author,
            text='Просто текст'
        )

        cls.another_user = User.objects.create_user(username='Другой автор')
        cls.another_note = Note.objects.create(
            title='Заметка другого автора',
            author=cls.another_user,
            text='Другой текст',
        )

    def test_custom_slug(self):
        """Тест на создание слага вручную."""
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
            slug='test-slug'
        )
        self.assertEqual(note.slug, 'test-slug')

    def test_sorted_notes(self):
        """Тест соритровки заметок."""
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        id_notes = [note.id for note in object_list]
        sorted_id = sorted(id_notes)
        self.assertEqual(id_notes, sorted_id)

    def test_note_in_context_object_list(self):
        """Тест передачи отдельной заметки на страницу со списком заметок."""
        self.client.force_login(self.another_user)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertIn(self.another_note, object_list)

    def test_author_only_sees_their_notes(self):
        """Тест отображения в заметках только заметок пользователя."""
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.another_note, object_list)

    def test_other_user_cant_see_other_note(self):
        """Тест отображения в заметках только заметок другого пользователя."""
        self.client.force_login(self.another_user)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertIn(self.another_note, object_list)
        self.assertNotIn(self.note, object_list)

    def test_form_on_add_and_edit_pages(self):
        """Тест на передачу форм для страниц редактирования и создания."""
        self.client.force_login(self.author)
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,))
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
