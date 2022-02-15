#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module saves and loads data for application.py.

Attributes:
    DEFAULT_RECORDS_FILENAME (str): Default path for storing and retrieving data.
    DEFAULT_STORAGE_LOG_FILENAME (str): Default file path for logging when this module is called directly.
    STORAGE_LOG_LEVEL (:obj: 'int'): Integer represents a value which assigns a log level from logging.

TODO:
    Possible revamp of ids using uuid.uuid4 to generate ids as strings.
    Possibly change ID_DIGIT_LENGTH to a range, and produce number between a min and max.
    Develop way to track deleted ids.
"""

import copy
import logging
from logging import handlers
from pathlib import Path
from random import randint

import yaml

from core import ID_DIGIT_LENGTH, RUNTIME_ID, _Template
from test_assets import create_mock_templates

DEFAULT_RECORDS_FILENAME = "records.yaml"
DEFAULT_STORAGE_LOG_FILENAME = "storage.log"
STORAGE_LOG_LEVEL = logging.DEBUG


# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StorageError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Repo:
    """Load and save program data."""

    # List of template class names.
    #   Example:
    #       self.subclass_names = ['Surgery', 'ComprehensiveExam', 'etc']
    subclass_names = [cls.__name__ for cls in _Template.__subclasses__()]

    # Keys = Template class, values = [empty].
    #   Construct dictionary format for use with self.templates.
    #   Example:
    #       self.classes = {
    #           'LimitedExam': [],
    #           'Surgery': [],
    #           'HygieneExam': [],
    #           'PeriodicExam': [],
    #           'ComprehensiveExam': []
    #       }
    classes = {_class: [] for _class in subclass_names}

    #   Gather _Template child class objects and insert them into a list.
    #   Example:
    #       subclass_obj = [<class 'core.LimitedExam'>, <class 'core.Surgery'>, <class 'core.HygieneExam'>, etc.]
    subclass_obj = _Template.__subclasses__()

    #   Dictionary of template class names as keys and corresponding objects as values.
    #   Example:
    #       self.note_classes = {
    #           'LimitedExam': <class 'core.LimitedExam'>,
    #           'Surgery': <class 'core.Surgery'>,
    #           'HygieneExam': <class 'core.HygieneExam'>,
    #           'PeriodicExam': <class 'core.PeriodicExam'>,
    #           'ComprehensiveExam': <class 'core.ComprehensiveExam'>
    #       }
    note_classes = dict(zip(subclass_names, subclass_obj))

    def __init__(self):
        """Initialize class."""
        log.debug("Initializing...")

        # Dictionary: keys=template class names, values=[note templates].
        #   Values will be populated with loaded data.
        #   Example:
        #       self.templates = {
        #           'LimitedExam': [LimitedExam objects],
        #           'Surgery': [Surgery objects],
        #           'HygieneExam': [HygieneExam objects],
        #           'PeriodicExam': [PeriodicExam objects],
        #           'ComprehensiveExam': [ComprehensiveExam objects]
        #       }
        self.templates = copy.deepcopy(self.classes)

        # List storing template id's for each note template.
        self.ids = []

        log.debug("Initializing complete.")

    def load_test(self):
        """Loads creates test data and loads into program.

        Intended for use with unittest.

        Args:
            None

        Returns:
            None
        """

        log.debug("Generating test data...")

        # Get list[Dict], where each dictionary is a representation of a note containing test data.
        notes = create_mock_templates(self.subclass_names)

        log.debug("Generation of test data complete.")
        log.debug("Instantiating test data...")

        self._load_obj(notes)

        log.debug("Instantiation of test data complete.")

    def load(self, file_path=DEFAULT_RECORDS_FILENAME):
        """Load note templates from data file.

        Args:
            file_path (str): File path with which to load program data. Must be .yaml file.

        Returns:
            None
        """

        log.debug("Loading...")

        templates = self._get_from_yaml(file_path)  # List of dictionaries representing each template.
        self._load_obj(templates)

        log.debug("Loading complete.")

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

        log.debug(f"Retrieving data from {file_path}...")

        # Check if .yaml data file exists. Create file if False.
        data_file = Path(file_path)
        data_file.touch(exist_ok=True)

        records = []
        with data_file.open(mode="r") as infile:
            try:
                records = yaml.full_load(infile)
                log.debug(f"Retrieving data from {file_path} complete.")
            except yaml.parser.ParserError as e:
                log.exception(f"{file_path} is not valid yaml, continuing with empty list")

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

        log.debug("Instantiating template objects...")

        for template in templates:
            self._instantiate_templates(template)

        log.debug("Instantiating template objects complete.")

    def _instantiate_templates(self, template):
        """Instantiate a note template object and append it to self.templates.

        Args:
            template (dict): Dictionary representing a note template.
                Example:
                    template = {'_type': 'Surgery', 'id': 0123456789, 'note': 'This is a note.'}

        Returns:
            note (Obj): Object representing a note template.
        """

        class_ = self.note_classes[template["_type"]]  # Identify class object.
        note = class_(template)  # Instantiate class object.

        self._add_id(template["id"])  # Add id to used id list (self.id_).

        try:  # Add add object to self.note_templates.
            self.templates[template["_type"]].append(note)
        # catch the likely errors and reraise
        except (KeyError, ValueError) as se:
            raise StorageError(f"Unable to instantiate templates for {template['id']}") from se
        # catch anything else and raise separately
        except BaseException as be:
            raise StorageError(f"Unexpected error instantiating templates for {template['id']}") from be

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
            msg = f"Error for ID #: {id_}. Must be {ID_DIGIT_LENGTH}."
            log.warning(msg)
            raise StorageError(msg)

        # Check if already used.
        elif id_ in self.ids:
            msg = f"Error for ID #: {id_}. ID already in use for another note template."
            log.warning(msg)
            raise StorageError(msg)

        # Check if id is an integer.
        elif type(id_) is not int:
            msg = f"Error for ID #: {id_}. ID must be an integer."
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

        log.debug(f"Saving data to {file_path}...")

        templates = self.templates
        records = []

        for k, v in templates.items():
            for note in v:  # Isolate individual template objects.
                record = note.to_dict()
                records.append(record)

        self._save_to_yaml(records, file_path)

        log.debug(f"Saving data to {file_path} complete.")

        return True

    def _save_to_yaml(self, records, file_path):
        """Save data to .yaml file.

        Args:
            records (lst [dict]): First parameter. List of dictionaries representing note templates.
                Example:
                    records = [
                        {'_type': 'Surgery', 'id': 0123456789, 'note': 'This is a note.'},
                        {'_type': 'Hygiene', 'id': 1234567890, 'note': 'This is another note.'}
                    ]

            file_path (str): Second parameter. File path within which to save data. Must be a yaml file.

        Returns:
            None
        """

        # Check legality of file type.
        if file_path.split(".")[1] != "yaml" and file_path.split(".")[1] != "yml":
            msg = (
                f"An error occurred while attempting to save to .yaml file. File path: {file_path} must end in "
                f".yaml, or .yml to be a legal yaml file."
            )
            log.warning(msg)
            raise StorageError(msg)

        with open(file_path, "w") as yaml_outfile:
            yaml.dump(records, yaml_outfile)

    def delete_note(self, id_):
        """Delete note.

        Args:
            id_ (int OR str): id number for note template to delete.

        Returns:
            (Bool): True if successful.
        """

        log.debug("Deleting note...")

        if type(id_) is str:  # Check legality of id_.
            if not id_.isnumeric():
                msg = f"Entered id: ({id_}), is not valid. Must only contain numbers."
                log.warning(msg)
                raise StorageError(msg)
            else:
                id_ = int(id_)

        if not type(id_) is int:  # Check legality of id_ argument.
            msg = "Entered id is not valid. Must be numeric."
            log.warning(msg)
            raise StorageError(msg)

        for name, notes in self.templates.items():
            for note in notes:
                if note.id == id_:
                    index = self.templates[name].index(note)
                    self.templates[name].pop(index)
                    self.ids.remove(id_)
                    msg = f"Template Type: {name}, id: {id_}, has been deleted."
                    log.debug(msg)
                    return True

        msg = f"Template id: {id_}, cannot be found and has NOT been deleted."
        log.debug(msg)
        raise StorageError(msg)

    def get_note(self, id_):
        """Return desired note.

        Finds note by matching ids.

        Args:
            id_ (int OR str): id number for desired template.

        Returns:
            note (_Template): Returns the note with a id that matches argument.
        """

        log.debug("Finding note...")

        if type(id_) is str:  # Check legality of id_ argument.
            if not id_.isnumeric():
                msg = "Entered id is not valid. Must be all numbers."
                log.warning(msg)
                raise StorageError(msg)
            else:
                id_ = int(id_)

        for name, notes in self.templates.items():
            for note in notes:
                if note.id == id_:
                    msg = "Note found."
                    log.debug(msg)
                    return note

        msg = f"Note with id: {id_}, cannot be found."
        log.debug(msg)
        raise StorageError(msg)

    def get_notes_of_type(self, type_):
        """Return all notes of type in argument.

        Args:
            type_ (str): Type.

        Returns:
            notes (lst): All notes of argument type.
        """

        log.debug(f"Retrieving all notes of type: {type_}.")

        if type_ not in self.templates.keys():
            msg = f"Could not find type: {type_} in stored notes."
            log.warning(msg)
            raise StorageError(msg)
        else:
            notes = [note for note in self.templates[type_]]
            log.debug(f"All notes of type: {type_} retrieved.")
            return notes

    def edit_type(self, note, desired_type):
        """Change the type of a note.

        Original id will be kept.

        Args:
            note (_Template): First argument. Note on which to change type.
            desired_type (_Template): Second argument. _Template subclass in which to change the first argument.

        Returns:
            edited (_Template): Note with class determined from new_type argument.
        """

        log.debug("Editing note type...")

        # Check legality of desired_type.
        if desired_type not in [cls for cls in self.note_classes.values()]:
            msg = f"Desired type: {desired_type.__class__.__name__}, is not an available type."
            log.warning(msg)
            raise StorageError(msg)

        # Check legality of note.
        if not isinstance(note, _Template):
            msg = f"Note to edit: {note}, is not a legal object."
            log.warning(msg)
            raise StorageError(msg)

        note_attrs = copy.deepcopy(note.to_dict())  # Note is dict.

        # Remove note original object.
        self.delete_note(note_attrs["id"])

        # Identify string name for desired_type.
        new_type = None
        for k, v in self.note_classes.items():
            if v == desired_type:
                new_type = k
                break

        note_attrs["_type"] = new_type

        # Add edited note.
        note = self._instantiate_templates(note_attrs)  # Note is obj.

        log.debug("Editing of note type is complete.")

        return note

    def generate_id(self):
        """Generate a unique id.

        Args:
            None

        Returns:
            id_ (int): A unique id number of the proper length (ID_DIGIT_LENGTH).
        """

        log.debug("Generating new id number...")

        is_unique = False
        is_long_enough = False
        while not is_unique or not is_long_enough:
            id_ = randint(int("1" + ("0" * (ID_DIGIT_LENGTH - 1))), int("9" * ID_DIGIT_LENGTH))
            #   Example if ID_DIGIT_LEN == 3:
            #       id_ = int between 100 & 999.

            if len(str(id_)) == ID_DIGIT_LENGTH:
                is_long_enough = True

            if id_ not in self.ids:
                is_unique = True

            if id_ is False or is_unique is False:
                id_, is_unique = False, False

        log.debug("New id number generated.")

        return id_


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


if __name__ == "__main__":

    # Configure Rotating Log. Only runs when module is called directly.
    handler = handlers.RotatingFileHandler(filename=DEFAULT_STORAGE_LOG_FILENAME, maxBytes=100**3, backupCount=1)
    formatter = logging.Formatter(f"[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(STORAGE_LOG_LEVEL)

    storage_self_test()
    # test()
