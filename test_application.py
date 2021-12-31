#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module is used to test notekeeperapp.py"""

import random
import unittest

from core import _Template, ID_DIGIT_LENGTH
from notekeeper import NoteKeeper
from test_assets import create_mock_templates


class TestApplication(unittest.TestCase):
    """Test application.py."""

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.app = NoteKeeper(test_=True)
        self.cls_names = [k for k in self.app.note_classes.keys()]  # Generate list of note class names.

    def tearDown(self):
        pass

    def test_create_note(self):
        """Test Application.create_note().

        Asserts that the template object is added correctly be checking the length of the template object list for the
        corresponding template type before and after it is added, and asserts that the template is instantiated into the
        correct object parent and child classes.
        """

        template = create_mock_templates(classes=self.cls_names, num=1)[0]
        len_before = len(self.app.templates[template['_type']])
        note = self.app.create_note(template)
        len_after = len(self.app.templates[template['_type']])

        self.assertEqual(len_before + 1, len_after)
        self.assertIn(note, self.app.templates[template['_type']])
        self.assertIsInstance(note, self.app.note_classes[template['_type']])
        self.assertIsInstance(note, _Template)

    def test_create_from_attributes(self):
        """Test Application.create_from_attributes().

        Asserts that the template object is added correctly be checking the length of the template object list for the
        corresponding template type before and after it is added, and asserts that the template is instantiated into the
        correct object parent and child classes.
        """

        template = create_mock_templates(classes=self.cls_names, num=1)[0]
        len_before = len(self.app.templates[template['_type']])
        note = self.app.create_from_attributes(type_=template['_type'], notes=template['note'])
        len_after = len(self.app.templates[template['_type']])

        self.assertEqual(len_before + 1, len_after)
        self.assertIn(note, self.app.templates[template['_type']])
        self.assertIsInstance(note, self.app.note_classes[template['_type']])
        self.assertIsInstance(note, _Template)

    def test_generate_id(self):
        """Test Application.generate_id()

        Asserts that the id generated is of the required length and type."""

        id_ = self.app.generate_id()
        self.assertEqual(len(str(id_)), ID_DIGIT_LENGTH)
        self.assertTrue(type(id_), type(int))

    def test_delete_note(self):
        """Test Application.delete_note().

        Picks a random note template from instance, asserts the existence of template, deletes template, and asserts the
        non existence to template. After testing, adds template object back into instance.
        """

        cls = random.choice(self.cls_names)
        template = random.choice(self.app.templates[cls])

        self.assertIn(template, self.app.templates[cls])
        len_before = len(self.app.templates[cls])
        self.app.delete_note(template.id)
        # Confirm object has been removed.
        self.assertNotIn(template, self.app.templates[cls])
        # Confirm that the appropriate list length has been reduced by 1.
        self.assertEqual(len_before, len(self.app.templates[cls]) + 1)

    def test_get_note(self):
        """Test Application.get_note().

        Assert Application.get_note() returns the correct note.
        """

        cls = random.choice(self.cls_names)
        note = random.choice(self.app.templates[cls])
        get_return = self.app.get_note(note.id)

        self.assertIs(note, get_return)

    def test_get_notes_of_type(self):
        """Test Application.get_notes_of_type().

        Asserts Application.get_notes_of_type() return notes of the required type."""

        cls = random.choice(self.cls_names)
        notes = self.app.get_notes_of_type(cls)

        for note in notes:
            self.assertIsInstance(note, self.app.get_class(note))
        self.assertEqual(len(notes), len(self.app.templates[cls]))

    def test_edit_note(self):
        """Test Application.edit_note().

        Tests that objects are edited properly by editing a template and confirming the proper changes are made.
        """

        cls = random.choice(self.cls_names)
        note = random.choice(self.app.templates[cls])

        new = create_mock_templates(self.cls_names, 1)[0]
        new['id'] = note.id
        note = self.app.edit_note(new)

        self.assertDictEqual(new, note.to_dict())
        self.assertIn(note, self.app.templates[new['_type']])

    def test_get_class(self):
        """Test Application.get_class().

        Tests that correct class is returned.
        """

        cls = random.choice(self.cls_names)
        note = random.choice(self.app.templates[cls])
        test = self.app.get_class(note)

        self.assertIsInstance(note, test)


if __name__ == '__main__':
    unittest.main()
