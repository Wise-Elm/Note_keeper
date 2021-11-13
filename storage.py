#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This module saves and loads data for application.py."""

import logging
from os.path import exists

import yaml

from core import _NoteTemplate
from core import ID_NUMBER_LENGTH


DEFAULT_RECORDS_FILENAME = 'records.yaml'


# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# TODO (GS): Get custom exception working.
class StorageError(RuntimeError):
    """Base class for exceptions arising from this module."""


class LoadingError(StorageError):
    """Exception class for loading errors."""


class SavingError(StorageError):
    """Exception class for saving errors."""


class Repo:
    """Load and save program data."""

    def __init__(self):

        log.debug('Initializing...')

        # Prepare self.notes with keys and empty lists corresponding to template classes.
        class_names = [cls.__name__ for cls in _NoteTemplate.__subclasses__()]  # Generate list of template class names.
        classes = {_class: [] for _class in class_names}  # Keys = Template class, values = [].
        self.note_templates = classes  # Dictionary: keys=template class names, values=[note templates].

        subclass_obj = _NoteTemplate.__subclasses__()  # Generate list of template class objects.
        # Generate dictionary of template class names as keys and objects as values.
        subclasses = dict(zip(class_names, subclass_obj))
        self.subclasses = subclasses  # Dictionary: keys=template class names, values=associated template class object.

        self._id = []  # List of storing template id's for each note template.

    def load(self, file_path=DEFAULT_RECORDS_FILENAME):
        """Load note templates from data file."""

        log.debug('Loading...')

        templates = self._get_from_yaml(file_path)  # List of dictionaries of each templates.
        self._load_obj(templates)

        log.debug('Loading complete.')

    def _get_from_yaml(self, file_path):
        """Retrieve data from yaml file.

        Args:
            file_path (str): Filepath for yaml file.

        Returns:
            patient_records (lst [dict]): List of dictionaries containing note templates.
        """

        log.debug(f'Retrieving data from {file_path}...')

        templates = []

        # Check if .yaml data file exists. Create file if False.
        file_exists = exists(file_path)  # Bool
        if not file_exists:
            new_file = open(file_path, 'w')
            new_file.close()

        with open(file_path, 'r') as infile:
            records = yaml.full_load(infile) or []
            for record in records:
                templates.append(record)

        log.debug(f'Retrieving data from {file_path} complete.')

        return records

    def _load_obj(self, templates):
        """Iterate through dictionary records.

        Args:
            templates (lst [dict]): List of each note template represented as a dictionary.

        Returns:
            None
        """

        log.debug('Instantiating template objects...')

        for template in templates:
            self._instantiate_templates(template)

        log.debug('Instantiating template objects complete.')

    def _instantiate_templates(self, template):
        """Instantiate template objects.

        Populate self.note_templates with template objects, self.subclasses with _Note subclass objects, and self._id
        with object id numbers.

        Args:
            template (dict): Dictionary representing a note template.

        Returns:
            note (Obj): Object representing a note template.
        """

        # Instantiate object.
        _class = self.subclasses[template['_type']]
        note = _class(template)

        try:  # Add add object to self.note_templates.
            self.note_templates[template['_type']].append(note)
        except ValueError(LoadingError) as e:
            log.critical('{}: Unable to instantiate template object for {}'.format(e, template['id']))

        # try:  # Add template id to self._id. Error is id is already in self._id.
        #     self._add_id(template['id'])
        # except LoadingError as e:
        #     log.critical('{}: Unable to add new template id.{}'.format(e, template['id']))

        self._add_id(template['id'])

        return note

    def _add_id(self, _id):
        """Add template id to repo._id if unique. Return False otherwise.

        Makes sure template id is not already in repo._id and confirms proper length for id number.

        Args:
            _id (int): 10 digit id number.

        Returns:
            None
        """

        if len(str(_id)) != ID_NUMBER_LENGTH or _id in self._id:
            error = LoadingError('Template id could not be loaded into repo._id')
            log.critical(f'{error}')
        else:
            self._id.append(_id)

    def save(self, templates, file_path=DEFAULT_RECORDS_FILENAME):
        """Save data to source file.

        Convert template objects to dictionary representations and store data.

        Args:
            templates (dict): The first parameter. Dictionary of template objects.
            file_path (str, OPTIONAL): The Second parameter. An optional file path with a default if left blank.

        Returns:
            None
        """

        log.debug(f'Saving data to {file_path}...')

        records = []

        for k, v in templates.items():
            for note in v:
                record = note.to_dict()
                records.append(record)

        self._save_to_yaml(records, file_path)

        log.debug(f'Saving data to {file_path} complete.')

    def _save_to_yaml(self, records, file_path):
        """Save to .yaml file.

        Args:
            records (lst [dict]): First parameter. List of dictionaries representing note templates.
            file_path (str): Second parameter. String for .yaml file path.

        Returns:
            None
        """

        with open(file_path, 'w') as yaml_outfile:
            yaml.dump(records, yaml_outfile)


def self_test():
    """Run Unittests on module.

        Runs when storage.py is called directly. Creates a new yaml file with random records for testing. Conducts
        testing with Unittest, and deletes test file when complete.

    Args:
        None

    Returns:
        None
    """

    import os
    import unittest

    import test_storage
    from test_storage import create_random
    from test_storage import TESTING_RECORDS_FILENAME

    repo = Repo()

    # Create test file.
    records = create_random(20)  # Generate random records.
    test_file = open(TESTING_RECORDS_FILENAME, 'w')
    repo._save_to_yaml(records, TESTING_RECORDS_FILENAME)  # Save random records to test yaml file.
    test_file.close()

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_storage)
    unittest.TextTestRunner(verbosity=2).run(suite)

    # Delete test file.
    os.remove(TESTING_RECORDS_FILENAME)


def test():
    """Used to perform detailed module testing during development. Not for production use.

    Args:
        None

    Returns:
        None
    """

    pass


if __name__ == '__main__':
    self_test()
    # test()
