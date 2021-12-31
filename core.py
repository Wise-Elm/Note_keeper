#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module provides object classes for application.py.

Attributes:
    RUNTIME_ID (:obj: 'UUID'): Designates an id for each runtime. Uses uuid4.
    ID_DIGIT_LENGTH (int): Designates length of note ids. Used over multiple modules when creating ids.
    DEFAULT_CORE_LOG_FILENAME (str): Default file path for logging when this module is called directly.
    CORE_LOG_LEVEL (:obj: 'int'): Integer represents a value which assigns a log level from logging.
"""

import copy
import logging
from logging import handlers
import uuid

RUNTIME_ID = uuid.uuid4()  # Set unique id for each runtime.
ID_DIGIT_LENGTH = 10
DEFAULT_CORE_LOG_FILENAME = 'core.log'  # Used when __name__ == '__main__'
CORE_LOG_LEVEL = logging.DEBUG

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CoreError(RuntimeError):
    """Base class for exceptions arising from this module."""


class _Template:
    """ABC. Objects of this type represent a periodontal appointment note template."""

    def __init__(self, template):
        self.id = template['id']  # type(int). Unique identification number.
        self.note = template['note']  # type(str). Exam note.
        """Initialize class.
        
            Args:
                template (dict): Note template.
                    Example:
                        template = {
                            'id': 0123456789,
                            'note': 'This is an example'
                        }
                
            Returns:
                None
        """

    def __repr__(self):
        """String representation of _Template containing technical information.

            Args:
                None

            Returns:
                result (str): String representation of self containing subclass name and id.
        """

        result = f'{self.__class__.__name__}, id: {self.id}'

        return result

    def __eq__(self, other):
        """Return true if other is deemed equal to self.

        Compares argument exam id with self.

        Args:
            other (dict OR Obj): Dictionary representation of a note template OR a _NoteTemplate obj.

        Returns:
            is_equivalent (bool): True if equal, False otherwise.
        """

        log.debug('__eq__...')

        # Handle dictionary as argument.
        if type(other) is dict:
            if 'id' in other:
                if self.id == other['id']:
                    log.debug('__eq__ = True.')
                    return True
                else:
                    log.debug('__eq__ = False.')
                    return False
            else:
                msg = 'Invalid id. Dictionary must contain an id as a key.'
                log.debug('__eq__ ' + msg)
                raise CoreError(msg)

        # Handle _NoteTemplate as argument.
        elif isinstance(other, _Template):
            if self.id == other.id:
                log.debug('__eq__ = True.')
                return True
            else:
                log.debug('__eq__ = False.')
                return False

        # Handle illegal argument.
        else:
            msg = 'Invalid ID. Comparison could not be made.'
            log.debug('__eq__ ' + msg)
            raise CoreError(msg)

    def __str__(self):
        """Return a string formatted to display self.

        Args:
            None

        Returns:
            display_text (str): String representation of self.
                Example:
                    '
                    Type: Surgery
                    ID: 0123456789

                    This is the note.
                    '
        """

        _type = self.__class__.__name__  # Child class name as string.
        display_text = 'Type: {}\nID: {}\n\n{}'.format(_type, self.id, self.note)
        return display_text

    def to_dict(self):
        """Return a dictionary representation of _Template.

        Args:
            None

        Returns:
            note (dict): A dictionary of this object's attrs as keys, and their values.
                Example:
                    note = {
                        '_type': 'Surgery',
                        'id': 0123456789,
                        'note': 'This is an example'
                    }
        """

        log.debug(f'{self.__repr__()} to_dict...')

        note = self.__dict__
        note = copy.deepcopy(note)  # Keep integrity of __dict__.
        note['_type'] = self.__class__.__name__

        log.debug(f'{self.__repr__()} to_dict.')
        return note


class LimitedExam(_Template):
    """Child class of _Template. Objects of this type represent a limited note template."""


class Surgery(_Template):
    """Child class of _Template. Objects of this type represent a surgery note template."""


class HygieneExam(_Template):
    """Child class of _Template. Objects of this type represent a hygiene note template."""


class PeriodicExam(_Template):
    """Child class of _Template. Objects of this type represent a periodic note template."""


class ComprehensiveExam(_Template):
    """Child class of _Template. Objects of this type represent a comprehensive note template."""


def core_self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_core

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_core)
    unittest.TextTestRunner(verbosity=2).run(suite)


def test():
    """For development level module testing."""

    pass


if __name__ == '__main__':

    # Configure Rotating Log. Only runs when module is called directly.
    handler = handlers.RotatingFileHandler(filename=DEFAULT_CORE_LOG_FILENAME, maxBytes=100**3, backupCount=1)
    formatter = logging.Formatter(f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(CORE_LOG_LEVEL)

    core_self_test()
    # test()
