#!/usr/bin/env python
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
STORAGE_LOG_LEVEL = logging.DEBUG


# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StorageError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Repo:
    """Load and save program data."""

    def __init__(self):

        log.debug('Initializing...')

        self.subclass_names = [cls.__name__ for cls in _Template.__subclasses__()]  # List of template class names.
        #   Example:
        #       self.class_names = ['Surgery', 'ComprehensiveExam', 'etc']

        self.classes = {_class: [] for _class in self.subclass_names}  # Keys = Template class, values = [empty].
        #   Construct dictionary format for use with self.templates.
        #   Example:
        #       self.classes = {
        #           'LimitedExam': [],
        #           'Surgery': [],
        #           'HygieneExam': [],
        #           'PeriodicExam': [],
        #           'ComprehensiveExam': []
        #       }

        self.templates = self.classes  # Dictionary: keys=template class names, values=[note templates].
        #   Values will be populated with loaded data.

        subclass_obj = _Template.__subclasses__()
        #   Gather _Template child class objects and insert them into a list.
        #   Example:
        #       subclass_obj = [<class 'core.LimitedExam'>, <class 'core.Surgery'>, <class 'core.HygieneExam'>, etc.]

        self.note_classes = dict(zip(self.subclass_names, subclass_obj))
        #   Dictionary of template class names as keys and corresponding objects as values.
        #   Example:
        #       self.subclasses = {
        #           'LimitedExam': <class 'core.LimitedExam'>,
        #           'Surgery': <class 'core.Surgery'>,
        #           'HygieneExam': <class 'core.HygieneExam'>,
        #           'PeriodicExam': <class 'core.PeriodicExam'>,
        #           'ComprehensiveExam': <class 'core.ComprehensiveExam'>
        #       }

        self.ids = []  # List storing template id's for each note template.
        """Initialize class."""

        log.debug('Initializing complete.')

    def load(self, file_path=DEFAULT_RECORDS_FILENAME):
        """Load note templates from data file.

        Args:
            file_path (str): File path with which to load program data. Must be .yaml file.

        Returns:
            None
        """

        log.debug('Loading...')

        templates = self._get_from_yaml(file_path)  # List of dictionaries representing each template.
        self._load_obj(templates)

        log.debug('Loading complete.')

    def _get_from_yaml(self, file_path):
        """Retrieve data from yaml file.

        Args:
            file_path (str): Filepath for yaml file. New file will be constructed if it does not already exist.

        Returns:
            records (lst [dict]): List of dictionaries containing note template attributes.
                Example:
                    records = [
                        {'_type': 'LimitedExam', 'id': 0123456789, 'note': 'This is a note.'},
                        {'_type': 'Surgery', 'id': 1234567890, 'note': 'This is another note.'},
                    ]
        """

        log.debug(f'Retrieving data from {file_path}...')

        # Check if .yaml data file exists. Create file if False.
        file_exists = exists(file_path)  # Bool
        if not file_exists:
            new_file = open(file_path, 'w')
            new_file.close()

        with open(file_path, 'r') as infile:
            records = yaml.full_load(infile) or []

        log.debug(f'Retrieving data from {file_path} complete.')

        return records

    def _load_obj(self, templates):
        """Iterates through loaded data and feeds another method which instantiates template objects.

        Passes loaded data to self._instantiate_template() for object instantiation.

        Args:
            templates (lst [dict]): List of each note template represented as a dictionary.
                Example:
                        templates = [
                            {'_type': 'Surgery', 'id': 0123456789, 'note': 'This is a note.'},
                            {'_type': 'Hygiene', 'id': 1234567890, 'note': 'This is another note.'}
                        ]

        Returns:
            None
        """

        log.debug('Instantiating template objects...')

        for template in templates:
            self._instantiate_templates(template)

        log.debug('Instantiating template objects complete.')

    def _instantiate_templates(self, template):
        """Instantiate a note template object and append it to self.templates.

        Args:
            template (dict): Dictionary representing a note template.
                Example:
                    template = {'_type': 'Surgery', 'id': 0123456789, 'note': 'This is a note.'}

        Returns:
            note (Obj): Object representing a note template.
        """

        class_ = self.note_classes[template['_type']]  # Identify class object.
        note = class_(template)  # Instantiate class object.

        self._add_id(template['id'])  # Add id to used id list (self.id_).

        try:  # Add add object to self.note_templates.
            self.templates[template['_type']].append(note)
        except StorageError('Unable to instantiate template object for {}'.format(template['id'])) as se:
            log.warning(f'{se}')

        return note

    def _add_id(self, id_):
        """Add template id to repo._id if unique.

        Check legality of argument, then add to self.id_ if legal.

        Args:
            id_ (int): Number representing a note template id..

        Returns:
            None
        """

        # Check length.
        if len(str(id_)) != ID_DIGIT_LENGTH:
            msg = f'Error for ID #: {id_}. Must be {ID_DIGIT_LENGTH}.'
            log.warning(msg)
            raise StorageError(msg)

        # Check if already used.
        elif id_ in self.ids:
            msg = f'Error for ID #: {id_}. ID already in use for another note template.'
            log.warning(msg)
            raise StorageError(msg)

        # Add id if checks passed.
        else:
            self.ids.append(id_)

    def save(self, file_path=DEFAULT_RECORDS_FILENAME):
        """Save data to disc.

        Convert note objects to dictionary representations and store data.

        Args:
            file_path (str, OPTIONAL): File path within which to save data. Must be .yaml. If none given a default file
            path will be used.

        Returns:
            True (Bool): True when successful.
        """

        log.debug(f'Saving data to {file_path}...')

        try:

            templates = self.templates

            records = []

            for k, v in templates.items():
                for note in v:  # Isolate individual template objects.
                    record = note.to_dict()
                    records.append(record)

            self._save_to_yaml(records, file_path)

            log.debug(f'Saving data to {file_path} complete.')

            return True

        except RuntimeError:
            msg = f'An error occurred while saving data to {file_path}.'
            log.warning(msg)
            raise StorageError(msg)

    def _save_to_yaml(self, records, file_path):
        """Save data to .yaml file.

        Args:
            records (lst [dict]): First parameter. List of dictionaries representing note templates.
                Example:
                    records = [
                        {'_type': 'Surgery', 'id': 0123456789, 'note': 'This is a note.'},
                        {'_type': 'Hygiene', 'id': 1234567890, 'note': 'This is another note.'}
                    ]

            file_path (str): Second parameter. File path within which to save data.

        Returns:
            None
        """

        with open(file_path, 'w') as yaml_outfile:
            yaml.dump(records, yaml_outfile)

    def delete_note(self, id_):  # TODO (GS): be aware that old numbers should be tracked.
        """Delete note.

        Args:
            id_ (int OR str): id number for note template to delete.

        Returns:
            (Bool): True if successful.
        """

        log.debug('Deleting note...')

        if type(id_) is str:  # Check legality of id_.
            if not id_.isnumeric():
                msg = f'Entered id: ({id_}), is not valid. Must only contain numbers.'
                log.debug(msg)
                raise StorageError(msg)
            else:
                id_ = int(id_)

        if not type(id_) is int:  # Check legality of id_ argument.
            msg = 'Entered id is not valid. Must be numeric.'
            log.debug(msg)
            raise StorageError(msg)

        for name, notes in self.templates.items():
            for note in notes:
                if note.id == id_:
                    index = self.templates[name].index(note)
                    self.templates[name].pop(index)
                    msg = f'Template Type: {name}, id: {id_}, has been deleted.'
                    log.debug(msg)
                    return True

        msg = f'Template id: {id_}, cannot be found and has NOT been deleted.'
        log.debug(msg)
        raise StorageError(msg)

    def get_note(self, id_):
        """Return a note displayed in a nice readable format.

        Args:
            id_ (int): id number for desired template.

        Returns:
            note (_Template): Returns the note with a id that matches argument.
        """

        log.debug('Finding note...')

        for name, notes in self.templates.items():
            for note in notes:
                if note.id == id_:
                    msg = 'Note found.'
                    log.debug(msg)
                    return note

        msg = f'Note with id: {id_}, cannot be found.'
        log.debug(msg)
        raise StorageError(msg)

    def edit_note(self, new_attributes):  # TODO (GS): Develop from app.
        """Change the attributes of a note.

        Finds

        Args:
            new_attributes (dict): Dictionary of desired note attributes.

        """

        pass

def storage_self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_storage

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_storage)
    unittest.TextTestRunner(verbosity=2).run(suite)


def test():
    """Used to perform detailed module testing during development. Not for production use.

    Args:
        None

    Returns:
        None
    """

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
