#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This module saves and loads data for application.py."""

import logging
from os.path import exists

import yaml

from core import _Template
from core import ID_DIGIT_LENGTH
from core import RUNTIME_ID


DEFAULT_RECORDS_FILENAME = 'records.yaml'
STORAGE_LOG_FILENAME = 'storage.log'  # Used when __name__ == '__main__'
STORAGE_LOG_LEVEL = logging.DEBUG  # Used when __name__ == '__main__'


# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StorageError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Repo:
    """Load and save program data."""

    def __init__(self):

        log.debug('Initializing...')

        # Prepare self.notes with keys and empty lists corresponding to template classes.
        class_names = [cls.__name__ for cls in _Template.__subclasses__()]  # Generate list of template class names.
        self.subclass_names = class_names
        self.classes = {_class: [] for _class in class_names}  # Keys = Template class, values = [].
        self.note_templates = self.classes  # Dictionary: keys=template class names, values=[note templates].

        subclass_obj = _Template.__subclasses__()  # Generate list of template class objects.
        # Generate dictionary of template class names as keys and objects as values.
        subclasses = dict(zip(class_names, subclass_obj))
        self.subclasses = subclasses  # Dictionary: keys=template class names, values=associated template class object.

        self.id_ = []  # List storing template id's for each note template.

    def load(self, file_path=DEFAULT_RECORDS_FILENAME, _test=False):
        """Load note templates from data file."""
        # TODO (GS): fix docstring.
        log.debug('Loading...')

        if _test is True:
            self.note_templates = self.classes  # Reset self.note_templates by clearing template data.
        else:
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
        except StorageError('Unable to instantiate template object for {}'.format(template['id'])) as e:
            log.critical(f'{e}')

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

        if len(str(_id)) != ID_DIGIT_LENGTH:
            msg = f'Error for ID #: {_id}. Must be {ID_DIGIT_LENGTH}.'
            log.critical(msg)
            raise StorageError(msg)
        elif _id in self.id_:
            msg = f'Error for ID #: {_id}. ID already in use for another note template.'
            log.critical(msg)
            raise StorageError(msg)
        else:
            self.id_.append(_id)

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

        try:

            records = []

            for k, v in templates.items():
                for note in v:
                    record = note.to_dict()
                    records.append(record)

            self._save_to_yaml(records, file_path)

        except StorageError('Unable to save data to disc') as e:
            log.critical(f'{e}')

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


def storage_self_test():
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
    from test_storage import STORAGE_TESTING_RECORDS_FILENAME

    repo = Repo()

    # Create test file.
    records = create_random()  # Generate random records.
    test_file = open(STORAGE_TESTING_RECORDS_FILENAME, 'w')
    repo._save_to_yaml(records, STORAGE_TESTING_RECORDS_FILENAME)  # Save random records to test yaml file.
    test_file.close()

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_storage)
    unittest.TextTestRunner(verbosity=2).run(suite)

    # Delete test file upon completion.
    os.remove(STORAGE_TESTING_RECORDS_FILENAME)


def test():
    """Used to perform detailed module testing during development. Not for production use.

    Args:
        None

    Returns:
        None
    """

    r = Repo()
    r.load()

    pass


if __name__ == '__main__':

    # Used during development. Log only stores data from latest run of if __name__ == '__main__'.
    logging.basicConfig(
        level=STORAGE_LOG_LEVEL,
        format=f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - %(message)s',
        filename=STORAGE_LOG_FILENAME,
        filemode='w'
    )

    storage_self_test()
    # test()
