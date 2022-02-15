#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module is used to provide testing assets for test_application.py, test_storage.py, & test_core.py.

Description:
    The functions in this module provide functionality for creating mock note templates for testing. The most
    commonly used function will be create_mock_template(), which uses the other function, but the other functions
    can be used to construct specific parts of note templates.

Attributes:
    DEFAULT_MOCK_TEMPLATE_DIGIT_NUM (int): Default number of mock templates to produce.
    DEFAULT_MOCK_NOTE_MIN_LENGTH (int): Default max digit length when generating mock notes.
    DEFAULT_MOCK_NOTE_MAX_LENGTH (int): Default min digit length when generating mock notes.
"""

import random
import unittest
from random import randint

from core import ID_DIGIT_LENGTH

DEFAULT_MOCK_TEMPLATE_DIGIT_NUM = 10
DEFAULT_MOCK_NOTE_MIN_LENGTH = 500
DEFAULT_MOCK_NOTE_MAX_LENGTH = 3000

IDS = []  # Keep list of used ids to make sure create_random_id() generates unique ids.


class TestingError(RuntimeError):
    """Base class for exceptions arising from this module."""


def create_mock_templates(classes, num=DEFAULT_MOCK_TEMPLATE_DIGIT_NUM):
    """Creates note templates fill with randomized attributes.

    Intended to be used for unittest. Will create templates using each class in argument classes in order until each
    class has been used. Once each class type in classes has been used for a template, random template classes from
    classes will be used. This is intended for the purposes of creating at least one template for each available class.

    Args:
        classes (lst): First Parameter. Classes for which a note can me instantiated.
        num (int, OPTIONAL): Second Parameter. Number of templates to generate. Must be greater than 0. Defaults to
            DEFAULT_MOCK_TEMPLATE_NUM.

    Returns:
        notes (lst[dict]): Each dictionary contains a template of attributes intended to represent a note.
            Example:
                dict = {
                    '_type': 'SomeClass',
                    'id': 0123456789,
                    'note': 'This is a note example.'
                }
    """

    if num < 1:
        msg = f"Argument num: {num}, must be greater than 0."
        raise TestingError(msg)

    notes = []
    all_cls_represented = False
    cls_to_represent = 0

    # Loop creates a mock note for each _Template class, then creates mock notes with randomized classes.
    for n in range(num):
        if all_cls_represented is True:
            type_ = random.choice(classes)
        # If num >= the number of available note classes make sure each class is represented with a template.
        elif cls_to_represent >= len(classes):
            all_cls_represented = True
            type_ = random.choice(classes)
        else:
            type_ = classes[cls_to_represent]
            cls_to_represent += 1

        randomized_note = {
            "_type": type_,
            "id": create_mock_id(),
            "note": create_mock_note(),
        }

        notes.append(randomized_note)

    return notes


def create_mock_id(id_len=ID_DIGIT_LENGTH):
    """Generate a randomized template id number.

    Args:
        id_len (int, OPTIONAL): Defaults to ID_DIGIT_LENGTH. Number of digits for return id_.

    Returns:
        id_ (int): Id number. Length of id number. Defaults to ID_DIGIT_LENGTH.
    """

    is_unique = False
    is_proper_len = False
    while not is_unique or not is_proper_len:
        id_ = randint(int("1" + ("0" * (id_len - 1))), int("9" * id_len))
        #   Example if ID_DIGIT_LEN == 3:
        #       id_ = int between 100 & 999.

        if len(str(id_)) == id_len:  # Check length.
            is_proper_len = True

        if id_ not in IDS:
            is_unique = True

        # Reset is_unique and is_proper_len variables when checks are not passed.
        if is_proper_len is False or is_unique is False:
            id_, is_unique = False, False

    IDS.append(id_)  # Add id_ to list of used ids.
    return id_


def create_mock_note(min_len=DEFAULT_MOCK_NOTE_MIN_LENGTH, max_len=DEFAULT_MOCK_NOTE_MAX_LENGTH):
    """Generate a note filled with random alphabetical characters and spaces.

    Args:
        min_len (int, OPTIONAL): First parameter. Defaults to DEFAULT_MOCK_NOTE_MIN_LENGTH. Minimum character length for
             note.
        max_len (int, OPTIONAL): Second parameter. DEFAULT_MOCK_NOTE_MAX_LENGTH. Maximum character length for note.

    Returns:
        note (str): String of random alphabetical and space characters of length between min_len and max_len.
    """

    characters = "  abcdefghijklmnopqrstuvwxyz"
    note = ""
    for i in range(min_len, max_len):
        letter = random.choice(characters)
        note += letter

    return note


if __name__ == "__main__":
    unittest.main()
