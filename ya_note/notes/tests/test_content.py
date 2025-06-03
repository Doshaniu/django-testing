from django.contrib.auth import get_user_model
from notes.forms import NoteForm

from .base_class import BaseClass

User = get_user_model()

EXPECTED_QUANTITY_NOTES = 1


class TestNotesPage(BaseClass):

    def test_sorted_notes(self):
        """Тест соритровки заметок."""
        response = self.author_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        id_notes = [note.id for note in object_list]
        sorted_id = sorted(id_notes)
        self.assertEqual(id_notes, sorted_id)

    def test_note_in_context_object_list(self):
        """Тест передачи отдельной заметки на страницу со списком заметок."""
        response = self.another_user_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.another_note, object_list)

    def test_author_only_sees_their_notes(self):
        """Тест отображения в заметках только заметок пользователя."""
        response = self.author_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), EXPECTED_QUANTITY_NOTES)
        self.assertEqual(object_list[0], self.note)

    def test_other_user_cant_see_other_note(self):
        """Тест отображения в заметках только заметок другого пользователя."""
        response = self.another_user_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.another_note, object_list)
        self.assertNotIn(self.note, object_list)

    def test_form_on_add_and_edit_pages(self):
        """Тест на передачу форм для страниц редактирования и создания."""
        urls = (
            self.ADD_URL,
            self.EDIT_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
