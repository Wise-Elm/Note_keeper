#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This module is used to test application.py"""

import random
from random import randint
import unittest

import yaml

from application import Application

from core import ID_DIGIT_LENGTH
from core import _Template

from storage import Repo

APPLICATION_TESTING_RECORDS_FILENAME = 'application_test.yaml'

app = Application()
repo = Repo()
repo.load(APPLICATION_TESTING_RECORDS_FILENAME)
app.templates = repo.note_templates



def create_random(num=50):
    """Generate random note_templates for unittest.

    Args:
        num (int, OPTIONAL): Number of note templates to generate. Defaults to 20.

    Returns:
        notes (list [dict]): List of dictionaries representing note templates. keys='_type', 'id', 'note'.
    """

    subclasses = [cls.__name__ for cls in _Template.__subclasses__()]  # List of note template classes.
    notes = []

    for n in range(num):
        random_note = {
            '_type': _random_type(subclasses),
            'id': _random_id(),
            'note': _random_note_gen()
        }
        notes.append(random_note)

    return notes


def _random_id(_len=ID_DIGIT_LENGTH):
    """Generate and random id for create_random().

    Args:
        _len (int, OPTIONAL): Length of id number. Defaults to 10 digits.

    Returns:
        _id (int)
    """

    unique = False
    _len = False
    while not unique or not _len:
        _id = randint(int('1' + ('0' * (ID_DIGIT_LENGTH - 1))), int('9' * ID_DIGIT_LENGTH))

        if len(str(_id)) == ID_DIGIT_LENGTH:
            _len = True
        if _id not in app._id:
            unique = True

        if _id is False or unique is False:
            _id, unique = False, False

    return _id


def _random_type(subclasses):
    """Generate a random class for note template.

    Args:
        subclasses (list [template class names])

    Returns:
        choice (str): Random class chosen from subclasses.
    """

    choice = random.choice(subclasses)

    return choice


def _random_note_gen(min_len=500, max_len=3000):
    """Generate a random template note.

    Args:
        min_len (int, OPTIONAL): Minimum character length for note. Default to 500 characters.
        max_len (int, OPTIONAL): Maximum character length for note. Default to 3000 characters.

    Returns:
        note (str): String of random alphabetical and space characters of length between min_len and max_len.
    """

    letters = '  abcdefghijklmnopqrstuvwxyz'
    note = ''
    for i in range(min_len, max_len):
        letter = random.choice(letters)
        note += letter
    return note


class TestApplication(unittest.TestCase):
    """Test application.py."""

    def test_add_template(self):
        """Test Application.add_template()."""

        new_template = create_random(1)[0]

        len_before = len(app.templates[new_template['_type']])
        new_template_obj = app.add_template(new_template)  # Note template object.
        len_after = len(app.templates[new_template['_type']])

        self.assertEqual(len_before+1, len_after)
        self.assertIsInstance(new_template_obj, app.subclasses[new_template['_type']])

    def test_display_template(self):
        """Test Application.display_template()."""

        random_name = random.choice(app.subclass_names)
        random_obj = random.choice(app.templates[random_name])
        first_template = random_obj.__str__()
        second_template = app.display_template(random_obj.to_dict()['_type'], random_obj.id)

        # index 0 on second template since display_template() has multiple returns.
        self.assertEqual(first_template, second_template[0])

    def test_delete_template(self):
        """Test Application.delete_template()."""

        test_template = random.choice(app.subclass_names)
        x = app.templates  # TODO(GS): Why is app.templates keys often empty?
        test_template = random.choice(app.templates[test_template])

        # Confirm length of list before object is removed.
        self.assertIn(test_template, app.templates[test_template.__class__.__name__])

        first_len = len(app.templates[test_template.__class__.__name__])
        app.delete_template(test_template.__class__.__name__, test_template.id)

        # Confirm object has been removed.
        self.assertNotIn(test_template, app.templates[test_template.__class__.__name__])
        # Confirm that the list the object was in is now one shorter.
        self.assertEqual(first_len, len(app.templates[test_template.__class__.__name__]) + 1)

    def test_edit_template(self):
        """Test Application.edit_template()."""

        _type = random.choice(app.subclass_names)
        pick = random.choice(app.templates[_type])

        modified_template = {
            '_type': _type,
            'id': pick.id,
            'note': 'This is a test'
        }

        result = app.edit_template(modified_template)

        # Confirm accuracy of edited note template.
        self.assertDictEqual(modified_template, result.to_dict())

        # Find original edited template.
        for template in app.templates[_type]:
            if template.id == modified_template['id']:
                new_template = template

        # Confirm edited note template was added to Application.template correctly.
        self.assertDictEqual(modified_template, new_template.to_dict())



if __name__ == '__main__':
    unittest.main()
