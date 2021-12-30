#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module performs a unittest on core.py"""

import random
import unittest

from core import _Template, CoreError
from notekeeper import NoteKeeper


class TestCore(unittest.TestCase):
    """Perform unittest on core.py."""

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

    def test_child_classes(self):
        """Test instantiation of _Template child classes."""

        for cls, notes in self.app.templates.items():
            for note in notes:
                self.assertIsInstance(note, self.app.get_class(note))

    def test_parent_class(self):
        """Test instantiation of _Template class."""

        for cls, notes in self.app.templates.items():
            for note in notes:
                self.assertIsInstance(note, _Template)

    def test__repr__(self):
        """Test _Template __repr__."""

        cls = random.choice(self.cls_names)
        note = random.choice(self.app.templates[cls])
        template = note.to_dict()

        msg = f"{template['_type']}, id: {template['id']}"
        self.assertEqual(note.__repr__(), msg)

    def test__str__(self):
        """Test _Template __str__."""

        cls = random.choice(self.cls_names)
        note = random.choice(self.app.templates[cls])
        template = note.to_dict()

        msg = f"Type: {template['_type']}\nID: {template['id']}\n\n{template['note']}"
        self.assertEqual(note.__str__(), msg)

    def test_to_dict(self):
        """Test _Template to_dict."""

        cls = random.choice(self.cls_names)
        note = random.choice(self.app.templates[cls])
        template = {'_type': cls, 'id': note.id, 'note': note.note}

        self.assertDictEqual(note.to_dict(), template)

    def test__eq__(self):
        """Test _Template __eq__."""

        cls = random.choice(self.cls_names)
        note = random.choice(self.app.templates[cls])

        # Confirm note is the same object as note.
        self.assertIs(note, note)

        # Confirm equality using object as argument.
        self.assertTrue(note.__eq__(note))
        # Confirm equality using dictionary as argument.
        self.assertTrue(note.__eq__(note.to_dict()))

        # Select new class, making sure it is not the same as cls.
        classes_ = [k for k in self.app.templates.keys() if k != cls]
        different_cls = random.choice(classes_)

        # Select another note.
        note_2 = random.choice(self.app.templates[different_cls])

        # Confirm inequality using object as argument.
        self.assertFalse(note.__eq__(note_2))
        # Confirm inequality using dictionary as argument.
        self.assertFalse(note.__eq__(note_2.to_dict()))

        # Test CoreError.

        # Bad argument.
        arg = 'asdf'
        with self.assertRaises(CoreError):
            note.__eq__(arg)

        # Dictionary without id.
        note_2 = note_2.to_dict()
        note_2.pop('id')
        with self.assertRaises(CoreError):
            note.__eq__(note_2)


if __name__ == '__main__':
    unittest.main()