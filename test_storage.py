#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module performs a unittest on storage.py

Attributes:
    DEFAULT_STORAGE_TEST_FILENAME (str):  Default path for storing and retrieving test data.
"""

import copy
import os
import random
import unittest

import yaml

from core import ID_DIGIT_LENGTH
from storage import Repo, StorageError
from test_assets import DEFAULT_MOCK_TEMPLATE_DIGIT_NUM


DEFAULT_STORAGE_TEST_FILENAME = "test_storage.yaml"


class TestStorage(unittest.TestCase):
    """Perform unittest on storage.py."""

    @classmethod
    def setUpClass(cls):
        repo = Repo()  # Instantiate Repo().
        repo.load_test()  # Load test data.
        repo.save(DEFAULT_STORAGE_TEST_FILENAME)  # Save test data to test file.

    @classmethod
    def tearDownClass(cls):
        os.remove(DEFAULT_STORAGE_TEST_FILENAME)  # Remove test file.

    def setUp(self):
        self.repo = Repo()
        self.repo.load(DEFAULT_STORAGE_TEST_FILENAME)

    def tearDown(self):
        pass

    def test_load_test(self):
        """Test Repo.load_test().

        Confirm the correct number of objects are loaded into the correct locations."""

        self.repo.ids = []
        self.repo.templates = (
            self.repo.classes
        )  # Reformat repo.templates to state before input data.

        self.assertEqual(len(self.repo.ids), 0)  # Confirm repo.ids is empty.
        self.assertDictEqual(
            self.repo.templates, self.repo.classes
        )  # Confirm that repo.templates in original state.

        self.repo.load_test()

        # Confirm proper number of ids are stored.
        self.assertEqual(len(self.repo.ids), DEFAULT_MOCK_TEMPLATE_DIGIT_NUM)
        for cls, notes in self.repo.templates.items():
            for note in notes:
                # Confirm that each note has been instantiated correctly.
                self.assertIsInstance(note, self.repo.note_classes[cls])

    def test_load(self):
        """Test Repo.load().

        Confirm that data is loaded properly by comparing successive reloads and checking loaded data against orininal
        data."""

        ids = copy.deepcopy(self.repo.ids)
        self.repo.ids = []  # Return to preloaded state.
        templates = copy.deepcopy(self.repo.templates)
        self.repo.templates = self.repo.classes  # Return to preloaded state.

        self.repo.load(DEFAULT_STORAGE_TEST_FILENAME)

        self.assertEqual(self.repo.ids, ids)
        self.assertDictEqual(self.repo.templates, templates)

        # Load test data.
        with open(DEFAULT_STORAGE_TEST_FILENAME, "r") as infile:
            records = yaml.full_load(infile) or []

        for cls, notes in self.repo.templates.items():
            for note in notes:
                # Confirm that each note has been instantiated correctly.
                self.assertIsInstance(note, self.repo.note_classes[cls])
                # Confirm that each note is in original loaded data.
                self.assertIn(note.to_dict(), records)

    def test_load_obj(self):
        """Test Repo.load_obj."""

        ids = copy.deepcopy(self.repo.ids)
        self.repo.ids = []  # Return to preloaded state.
        templates = copy.deepcopy(self.repo.templates)
        self.repo.templates = self.repo.classes  # Return to preloaded state.

        # Load test data.
        with open(DEFAULT_STORAGE_TEST_FILENAME, "r") as infile:
            records = yaml.full_load(infile) or []

        self.repo._load_obj(records)

        # Confirm loaded data is the same as existing data.
        self.assertEqual(self.repo.ids, ids)
        self.assertDictEqual(self.repo.templates, templates)

    def test_instantiate_templates(self):
        """Test Repo._instantiate_templates."""

        ids = copy.deepcopy(self.repo.ids)
        self.repo.ids = []  # Return to preloaded state.
        templates = copy.deepcopy(self.repo.templates)
        self.repo.templates = self.repo.classes  # Return to preloaded state.

        # Load test data.
        with open(DEFAULT_STORAGE_TEST_FILENAME, "r") as infile:
            records = yaml.full_load(infile) or []

        self.repo._instantiate_templates(records[0])

        # Confirm loaded data is the same as existing data.
        self.assertIn(self.repo.ids[0], ids)
        new_template = self.repo.templates[records[0]["_type"]][
            0
        ]  # Isolate record for testing.
        self.assertIn(new_template, templates[records[0]["_type"]])
        self.assertIsInstance(new_template, self.repo.note_classes[records[0]["_type"]])

    def test_add_id(self):
        """Test Repo._add_id()."""

        ids = self.repo.ids

        for id_ in ids:
            with self.assertRaises(StorageError):
                # Confirm exception is raised when attempting to add duplicate ids.
                self.repo._add_id(id_)

        for id_ in ids:
            id_too_long = int(str(id_) + "0")
            with self.assertRaises(StorageError):
                # Confirm exception is raised when attempting to add an id that has too many digits.
                self.repo._add_id(id_too_long)

        for id_ in ids:
            id_too_short = int(str(id_)[:-1])
            with self.assertRaises(StorageError):
                # Confirm exception is raised when attempting to add an id that has too many digits.
                self.repo._add_id(id_too_short)

        for id_ in ids:
            id_not_integer = str(id_)
            with self.assertRaises(StorageError):
                # Confirm exception is raised when attempting to add an id that is not type int.
                self.repo._add_id(id_not_integer)

        new_id = self.repo.generate_id()  # Generate a new legal id.
        self.repo._add_id(new_id)  # Add new id.
        self.assertIn(
            new_id, self.repo.ids
        )  # Confirm new id has been added to Repo.ids.

    def test_save(self):
        """Test Repo.save().

        Uses a saving and loading cycle to confirm integrity of data.
        """

        ids = copy.deepcopy(self.repo.ids)
        templates = copy.deepcopy(self.repo.templates)

        self.repo.save()
        self.repo.ids = []  # Return to preloaded state.
        self.repo.templates = self.repo.classes  # Return to preloaded state.
        self.repo.load()

        self.assertDictEqual(self.repo.templates, templates)
        self.assertEqual(self.repo.ids, ids)

    def test_save_to_yaml(self):
        """Test Repo._save_to_yaml()."""

        # Generate lis[dict] representing note data.
        records = []
        for k, v in self.repo.templates.items():
            for note in v:  # Isolate individual template objects.
                record = note.to_dict()
                records.append(record)

        # Test StorageError when trying to pass a non-yaml file type.
        with self.assertRaises(StorageError):
            self.repo._save_to_yaml(records, file_path="test_storage.txt")

        # Save data to yaml.
        self.repo._save_to_yaml(records, DEFAULT_STORAGE_TEST_FILENAME)

        # Retrieve data from yaml.
        with open(DEFAULT_STORAGE_TEST_FILENAME, "r") as infile:
            new_records = yaml.full_load(infile) or []

        # Confirm data has not changed.
        self.assertEqual(new_records, records)

    def test_delete_note(self):
        """Test Repo.delete_note()."""

        # Select random note to delete.
        cls = random.choice(self.repo.subclass_names)
        note = random.choice(self.repo.templates[cls])

        # Confirm the existence of note.
        self.assertIn(note, self.repo.templates[cls])

        self.repo.delete_note(note.id)  # Delete note.

        # Confirm that note and note id no longer exist.
        self.assertNotIn(note, self.repo.templates[cls])
        self.assertNotIn(note.id, self.repo.ids)

    def test_get_note(self):
        """Test Repo.get_note()."""

        # Select random note.
        cls = random.choice(self.repo.subclass_names)
        note = random.choice(self.repo.templates[cls])

        # Find note.
        note_2 = self.repo.get_note(note.id)

        # Confirm notes are the same.
        self.assertIs(note_2, note)

        # Test for StorageError.
        new_id_1 = self.repo.generate_id()  # Generate id that does not yet exist.
        with self.assertRaises(StorageError):
            self.repo.get_note(new_id_1)

        new_id_2 = str(note.id) + "a"  # Generate id that is not numeric.
        with self.assertRaises(StorageError):
            self.repo.get_note(new_id_2)

    def test_get_notes_of_type(self):
        """Test Repo.get_notes_of_type()."""

        # Select all notes of random type.
        cls = random.choice(self.repo.subclass_names)
        notes = self.repo.templates[cls]

        self.assertEqual(self.repo.get_notes_of_type(cls), notes)

        junk_cls = "asdf"
        with self.assertRaises(StorageError):
            self.repo.get_notes_of_type(junk_cls)

    def test_edit_type(self):
        """Test Repo.edit_type()."""

        # Select random note.
        cls = random.choice(self.repo.subclass_names)
        note = random.choice(self.repo.templates[cls])

        # Confirm that note is an instance of the proper class.
        self.assertIsInstance(note, self.repo.note_classes[cls])

        # Select new class, making sure it is not the same as cls.
        new_cls = ""
        same_cls = True
        while same_cls is True:
            new_cls = random.choice(self.repo.subclass_names)
            if new_cls != cls:
                same_cls = False

        # Edit note class.
        note = self.repo.edit_type(note, self.repo.note_classes[new_cls])

        # Confirm note is no longer in list for original class.
        self.assertNotIn(note, self.repo.templates[cls])
        # Confirm note is in list of new class.
        self.assertIn(note, self.repo.templates[new_cls])
        # Confirm note is an instance of the new class.
        self.assertIsInstance(note, self.repo.note_classes[new_cls])

        # Test StorageError.

        # Test for bad class.
        junk_cls = int
        with self.assertRaises(StorageError):
            self.repo.edit_type(note, junk_cls)

    def test_generate_id(self):
        """Test Repo.generate_id().

        A shortcoming of this test is that it cannot test for uniqueness of generated ids because of the large amount
        of ids that would need to be generated."""

        id_ = self.repo.generate_id()

        # Confirm the number of digits in id_ == ID_DIGIT_LENGTH.
        self.assertEqual(len(str(id_)), ID_DIGIT_LENGTH)
        # Confirm that id_ is type int.
        self.assertEqual(type(id_), int)
        # Confirm that id_ is not a duplicate (already in repo.ids).
        self.assertNotIn(id_, self.repo.ids)


if __name__ == "__main__":
    unittest.main()
