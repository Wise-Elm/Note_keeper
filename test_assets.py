#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This module is used to provide testing assets for test_application.py, test_storage.py, & test_core.py.

The functions in this module provide functionality for creating randomized note templates for testing."""

import random
from random import randint
import unittest

from core import ID_DIGIT_LENGTH


# TODO (GS): Fix docstring.
def create_random_template(app, num=10):
    """Generate random note_templates for unittest.

    Args:
        num (int, OPTIONAL): Number of note templates to generate. Defaults to 20.

    Returns:
        notes (list [dict]): List of dictionaries representing note templates. keys='_type', 'id', 'note'.
    """

    subclasses = app.subclass_names
    notes = []

    for n in range(num):
        random_note = {
            '_type': create_random_type(subclasses),
            'id': create_random_id(app),
            'note': create_random_note()
        }

        note = app.add_template(random_note, random_note['id'])  # Fill app.templates.
        notes.append(note)

    # Check to see if there are any missing note template types and fill them, only if the num argument is >= the number
    # of possible note template types.
    if num >= len(app.templates):
        for _type in app.templates:
            if len(app.templates[_type]) == 0:
                random_note = {
                    '_type': _type,
                    'id': create_random_id(app),
                    'note': create_random_note()
                }
                note = app.add_template(random_note, random_note['id'])  # Fill app.templates.
                notes.append(note)
    return app


def create_random_id(app, _len=ID_DIGIT_LENGTH):  # TODO (GS): Fix docstring.
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


def create_random_type(subclasses):
    """Generate a random class for note template.

    Args:
        subclasses (list [template class names])

    Returns:
        choice (str): Random class chosen from subclasses.
    """

    choice = random.choice(subclasses)

    return choice


def create_random_note(min_len=500, max_len=3000):
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


if __name__ == '__main__':
    unittest.main()
    # TODO (GS): Create a unittest for this module.
