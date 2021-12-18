#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module is used to provide testing assets for test_application.py, test_storage.py, & test_core.py.

The functions in this module provide functionality for creating randomized note templates for testing. The most
commonly used function will be create_random_template(), which uses all of the other function, but the other functions
can be used to construct specific parts of note templates."""

import random
from random import randint
import unittest

from core import ID_DIGIT_LENGTH


class TestingError(RuntimeError):
    """Base class for exceptions arising from this module."""


def create_random_templates(app=None, repo=None, num=10):
    """Generate randomized note templates for unittest and populate argument instance.

    One instance must be used, either app OR repo. Will either populate app.templates, OR repo.note_templates.

    Args:
        app (instance, OPTIONAL OR None): First parameter. Instance of Application class from application.py for
            application testing.
        repo (instance, OPTIONAL OR None): Second parameter. Instance of Repo class from storage.py for storage testing.
        num (int, OPTIONAL): Third parameter. Number of note templates to generate. Defaults to 10.

    Returns:
        app OR repo (instance): app instance if app!=None, or repo instance if repo!=None.

            Example of app instance after return. app.templates will be populated:
                app.templates = {
                    'LimitedExam': [LimitedExam objects],
                    'Surgery': [Surgery objects],
                    'HygieneExam': [HygieneExam objects],
                    'PeriodicExam': [PeriodicExam objects],
                    'ComprehensiveExam': [ComprehensiveExam objects]
                }
    """

    if app is not None and repo is not None:
        msg = 'Function can only accept either app OR repo as arguments, not both.'
        raise TestingError(msg)

    if app is None and repo is None:
        msg = 'Eight app OR repo MUST be passed as an argument.'
        raise TestingError(msg)

    if app:

        subclasses = app.subclass_names
        notes = []

        for n in range(num):
            random_note = {
                '_type': create_random_type(subclasses),
                'id': create_random_id(app=app),
                'note': create_random_note()
            }

            note = app.add_template(random_note, random_note['id'])  # Fill app.templates.
            notes.append(note)

        # Check to see if there are any missing note template types and fill them, only if the num argument is >= the
        # number of possible note template types.
        if num >= len(app.templates):
            for _type in app.templates:
                if len(app.templates[_type]) == 0:
                    random_note = {
                        '_type': _type,
                        'id': create_random_id(app=app),
                        'note': create_random_note()
                    }
                    note = app.add_template(random_note, random_note['id'])  # Fill app.templates.
                    notes.append(note)
        return app

    elif repo:

        subclasses = repo.subclass_names
        notes = []

        for n in range(num):
            random_note = {
                '_type': create_random_type(subclasses),
                'id': create_random_id(repo=repo),
                'note': create_random_note()
            }

            note = repo._instantiate_templates(random_note)  # Fill repo.note_templates.
            notes.append(note)

        # Check to see if there are any missing note template types and fill them, only if the num argument is >= the
        # number of possible note template types.
        if num >= len(repo.templates):
            for _type in repo.templates:
                if len(repo.templates[_type]) == 0:
                    random_note = {
                        '_type': _type,
                        'id': create_random_id(repo=repo),
                        'note': create_random_note()
                    }
                    note = repo._instantiate_templates(random_note)  # Fill repo.note_templates.
                    notes.append(note)
        return repo


def create_random_template(type_):
    """Create a single randomized template in the for of a dictionary.

    Args:
        type_ (str): String representing the name of a class.

    Returns:
        template (dict): Dictionary representing a randomized note template.
    """

    template = {
            '_type': type_,
            'id': create_random_id(),
            'note': create_random_note()
    }
    return template


def create_random_id(app=None, repo=None, id_len=ID_DIGIT_LENGTH):
    """Generate a random template id number.

    Will generate and return a legal template id if no instance is passed. Will populate an instance if an instance is
    passed. Only one instance can be passed at a time, either app or repo, and not both.

    Args:
        app (instance, OPTIONAL OR None): First parameter. Instance of Application class from application.py for
            application testing.
        repo (instance, OPTIONAL OR None): Second parameter. Instance of Repo class from storage.py for storage testing.
        id_len (int, OPTIONAL): Third parameter. Length of id number. Defaults to ID_DIGIT_LENGTH.

    Returns:
        id_ (int): Integer that is of length id_len, and is unique to the instance if an instance is passed.
    """

    if app is not None and repo is not None:
        msg = 'Function can only accept either app OR repo as arguments, not both.'
        raise TestingError(msg)

    unique = False
    len_ = False
    while not unique or not len_:
        id_ = randint(int('1' + ('0' * (id_len - 1))), int('9' * id_len))
        #   Example if ID_DIGIT_LEN == 3:
        #       id_ = int between 100 & 999.

        if len(str(id_)) == id_len:  # Check length.
            len_ = True

        if app is not None:  # If instance of app, check if id_ is a duplicate.
            if id_ not in app.id_:
                unique = True

        elif repo is not None:  # If instance of repo, check if id_ is a duplicate.
            if id_ not in repo.id_:
                unique = True

        elif app is None and repo is None:  # For generating an id outside of an instance, don't worry about uniqueness.
            unique = True

        if len_ is False or unique is False:  # Reset unique and len_ variables when checks are not passed.
            id_, unique = False, False

    return id_


def create_random_type(subclasses):
    """Generate a random class for a note template.

    Args:
        subclasses (lst [str]): List of legal class names.
            Example:
                subclasses = ['Surgery', 'ComprehensiveExam', 'etc']

    Returns:
        choice (str): Random class chosen from subclasses.
    """

    choice = random.choice(subclasses)

    return choice


def create_random_note(min_len=500, max_len=3000):
    """Generate a note filled with random alphabetical characters and spaces.

    Args:
        min_len (int, OPTIONAL): First parameter. Minimum character length for note. Default to 500 characters.
        max_len (int, OPTIONAL): Second parameter. Maximum character length for note. Default to 3000 characters.

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
