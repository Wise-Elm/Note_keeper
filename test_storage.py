#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This module performs a unittest on storage.py"""

import random
from random import randint
import unittest

import yaml

from core import _NoteTemplate
from core import ID_NUMBER_LENGTH

from storage import Repo
from storage import DEFAULT_RECORDS_FILENAME


repo = Repo()

TESTING_RECORDS_FILENAME = 'storage_test.yaml'


def create_random(num=20):
    """Generate random note_templates for unittest.

    Args:
        num (int, OPTIONAL): Number of note templates to generate. Defaults to 20.

    Returns:
        notes (list [dict]): List of dictionaries representing note templates. keys='_type', 'id', 'note'.
    """

    subclasses = [cls.__name__ for cls in _NoteTemplate.__subclasses__()]  # List of note template classes.
    notes = []

    for n in range(num):
        random_note = {
            '_type': _random_type(subclasses),
            'id': _random_id(),
            'note': _random_note_gen()
        }
        notes.append(random_note)

    return notes


def _random_id(_len=ID_NUMBER_LENGTH):
    """Generate and random id for create_random().

    Args:
        _len (int, OPTIONAL): Length of id number. Defaults to 10 digits.

    Returns:
        _id (int)
    """

    digit_len_check = False
    while not digit_len_check:
        _id = randint(0000000000, 9999999999)
        if len(str(_id)) == 10:
            digit_len_check = True
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


class TestStorage(unittest.TestCase):
    """Perform unittest on storage.py."""

    def test_object(self):
        """Test repo._instantiate_templates() to make sure objects are being instantiated correctly."""

        repo.load(TESTING_RECORDS_FILENAME)

        # Confirm that created objects are of the appropriate class.
        for objects, templates in repo.note_templates.items():
            for template in templates:
                self.assertIsInstance(template, repo.subclasses[objects])

    def test_yaml_data(self):
        """Test data in storage file as well as repo.load() for required dictionary keys and values."""

        test_records = []

        with open(DEFAULT_RECORDS_FILENAME, 'r') as infile:
            records = yaml.full_load(infile)
            for record in records:
                test_records.append(record)

        for record in test_records:
            self.assertIn('_type', record)
            self.assertIn('id', record)
            self.assertIn('note', record)

    def test_id_duplicates(self):
        """Test repo._id to make sure it is not storing duplicate values."""

        _id_2 = set(repo._id)  # Make a set version of repo._id to eliminate possible duplicates.
        self.assertEqual(len(repo._id), len(_id_2))

    def test_load_save(self):
        """Test one load and save cycle to confirm that data has not changed."""

        first_records = []

        with open(TESTING_RECORDS_FILENAME, 'r') as infile:
            records = yaml.full_load(infile)
            for record in records:
                first_records.append(record)

        # Cycle through instance of Repo and save to file.
        repo.load(TESTING_RECORDS_FILENAME)
        repo.save(repo.note_templates, TESTING_RECORDS_FILENAME)

        # Reload data from .yaml file and store in list.
        second_records = repo._get_from_yaml(TESTING_RECORDS_FILENAME)

        # Compare original data to new data.
        for record in first_records:
            self.assertIn(record, second_records)

        self.assertEqual(len(first_records), len(second_records))


if __name__ == '__main__':
    unittest.main()
