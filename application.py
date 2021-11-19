#!/usr/bin/python3
# -*- coding: utf-8 -*-

__version__ = '0.0.1'


"""Note retrieval application.

This application is designed to aid in writing patient notes for medical purposes. Note templates are intended to
provide the basic structure of a patient note so that the practitioner can save time by filling in the details. This
program provides the ability to create, display, edit, save, and delete note templates.

Todo:
    Configure a rotating log handler.
"""


import argparse
import sys
from datetime import date
import logging
from random import randint

from core import _NoteTemplate
from core import ID_DIGIT_LENGTH
from core import RUNTIME_ID

from storage import Repo
from storage import storage_self_test

LOG_FILENAME = 'application.log'
DEFAULT_LOG_LEVEL = logging.DEBUG

# Configure logging.
log = logging.getLogger(__name__)
log.setLevel(DEFAULT_LOG_LEVEL)


class ApplicationError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Application:
    """Handle interaction between program layers."""

    def __init__(self):

        self.repo = Repo()
        self.repo.load()

        self.templates = self.repo.note_templates  # Dictionary: keys=template class names, values=[note templates].
        self._id = self.repo.id_  # List storing template id's for each note template.
        # List of valid template classes.
        self.subclass_names = [cls.__name__ for cls in _NoteTemplate.__subclasses__()]
        # Dictionary: keys=template class names, values=associated template class object.
        self.subclasses = self.repo.subclasses

    def add_template(self, new_template, _id=None):
        """Add new note template.

        Adds key('id'): value(unique 10 digit number for identification).

        Args:
            new_template (dict): keys = '_type' & 'note".
            _id (int, OPTIONAL): Used to assign specific id number to new note template.

        Returns:
            template (obj): Note template object.
        """

        log.debug('Add new template...')

        # Check if new_template can be associated with a valid class.
        if new_template['_type'] not in self.subclass_names:
            msg = 'Note Template type not allowed. Input type: {}'.format(new_template['type'])
            log.critical(msg)
            raise ApplicationError(msg)

        # Format new_template Keys and values for inclusion into self.templates.
        if _id is None:
            _id = self._generate_random_id()

        output_template = {
            'id': _id,
            'note': new_template['note']
        }

        subclass_obj = _NoteTemplate.__subclasses__()  # Generate list of template class objects.
        # Generate dictionary of template class names as keys and objects as values.
        subclasses_w_obj = dict(zip(self.subclass_names, subclass_obj))

        _class = subclasses_w_obj[new_template['_type']]  # Select appropriate type for new_template.
        template = _class(output_template)  # Instantiate template object.

        # Add new object to appropriate dictionary value in self.templates.
        self.templates[str(template.__class__.__name__)].append(template)

        log.debug('New template added.')

        return template  # type object.

    def _generate_random_id(self):
        """Generate a random id number that has not been used.

        Args:
            None

        Returns:
            _id (int): A unique id number that has not been used and is of the specified length.
        """

        log.debug('Generate new id number...')

        unique = False
        _len = False
        while not unique or not _len:
            _id = randint(int('1' + ('0' * (ID_DIGIT_LENGTH - 1))), int('9' * ID_DIGIT_LENGTH))

            if len(str(_id)) == ID_DIGIT_LENGTH:
                _len = True
            if _id not in self._id:
                unique = True

            if _id is False or unique is False:
                _id, unique = False, False

        log.debug('New id number generated.')

        return _id

    def display_template(self, _type, _id):
        """Display desired note template.

        Args:
            _type (str): Template class type.
            _id (str OR int): id number for template.

        Returns:
            template (str) OR (None): Note template matching the id number and _type from arguments, or None when no
                stored template has a matching id number.
        """

        log.debug('Finding template to display...')

        if type(_id) is str:
            _id = int(_id)

        for template in self.templates[_type]:
            if template.id == _id:
                log.debug('Template found.')
                return template.text_display()

        # When template not found.
        msg = f'Template with type: {_type}, id: {_type} NOT found.'
        log.debug(msg)

        return None

    def display_all_of_type(self, _type):
        """Displays all note templates from specified type.

        Concatenates all from type together as one long string in the form of a text document.

        Args:
            _type (str): Type of note template.

        Returns:
            long_text (str): Formatted string containing all note templates from argument type.
        """

        log.debug('Compiling display data...')

        try:
            long_text = ''
            num = 1
            for template in self.templates[_type]:
                out_str = f'\n\nNumber: {num}\n' + template.text_display() + '\n'
                long_text += out_str
                num += 1

            log.debug('Display data compiled.')

            return long_text

        except:
            msg = 'Applicaiton.display_all_of_type() failed.'
            log.critical(msg)
            raise ApplicationError(msg)

    def delete_template(self, _type, _id):
        """Delete note template.

        Args:
            _type (str): Template type.
            _id (int OR str): id number for note template to delete.

        Returns:
            result (Bool): True if successful, False otherwise.
        """

        log.debug(f'Deleting template. Type: {_type}, id: {_id}...')

        if type(_id) is str:
            _id = int(_id)

        for template in self.templates[_type]:
            if template.id == _id:
                _index = self.templates[_type].index(template)
                self.templates[_type].pop(_index)
                log.debug(f'Template Type: {_type}, id: {_id}, has been deleted.')
                return True

        log.debug(f'Template Type: {_type}, id: {_id}, cannot be found and has NOT been deleted.')
        return False

    def edit_template(self, edited_template):
        """Edit note template attributes.

        Edit all attributes of a note template except the id number.

        Args:
            edited_template (dict): Dictionary of note template attributes.

        Returns:
            result (_NoteTemplate[obj] OR None): Object if successful, None otherwise.
        """

        log.debug('Editing note template...')

        result = None

        # Search same template type for matching ID. (Attempt a O(log(n)) search.)
        original_template = None  # Filled with original template if found within same note template type.
        for template in self.templates[edited_template['_type']]:  # Find template.
            if template.id == edited_template['id']:
                original_template = template
                break

        # If ID not found within note template type, search other template types. (Go ahead with O(N) search.)
        if original_template is None:
            for k, v in self.templates.items():
                if k == edited_template['_type']:  # Skip already searched template type.
                    continue
                else:
                    for template in v:
                        if template.id == edited_template['id']:
                            original_template = template
                            break

        if original_template is None:  # When template is not found.
            message = 'Template not found for ID: {}.'.format(edited_template['id'])
            log.debug(message)
            return result

        # Delete original template.
        self.delete_template(original_template.to_dict()['_type'], original_template.to_dict()['id'])

        # Add new template.
        result = self.add_template(new_template=edited_template, _id=edited_template['id'])

        log.debug('Note template has been edited.')

        return result

    def today_date(self):
        """Return datetime object representing today's date.

        Args:
            None

        Returns:
            today_date (datetime obj): datetime object.
        """

        log.debug("""Retrieve today's date...""")

        today_date = date.today()

        log.debug("""Today's date found.""")

        return today_date

    def save(self, templates):
        """Save application data.

        Args:
            templates (dict{k=type, v=list[note templates]}): Keys=template type: Values=List[note templates].

        Returns:
            None
        """

        log.debug('Saving...')

        self.repo.save(templates)

        log.debug('Saved.')


def parse_args(argv=sys.argv):
    """Run program from terminal."""

    log.debug('parse_args...')

    parser = argparse.ArgumentParser(description='Program for aiding in writing medical patient notes. Program provides'
                                                 ' the ability to add, edit, remove, etc., note templates. Note '
                                                 'templates provide a basic pre-written note to be used as the basis '
                                                 'for an indepth patient note.'
                                     )

    # Run Application.self_test().
    parser.add_argument(
        '-t',
        '--test',
        help='Run testing on application to confirm program is running correctly and exit. OK = Pass.',
        action='store_true',
        default=False
    )

    # Run Application.today_date().
    parser.add_argument(
        '-d',
        '--date',
        help="""Return today's date and exit.""",
        action='store_true',
        default=False
    )

    # Run Application.display_all_of_type().
    parser.add_argument(
        '-a',
        '--all',
        help='Display all note templates for argument type. Avaliable note types: Periodic, Hygiene, Surgery, '
             'Comprehensive, Limited.',
        nargs=1,
        default=False,
        metavar='Type.',
    )

    # Run Application.display_template().
    parser.add_argument(
        '-w',
        '--display',
        help='Display a specific note template. Args=(type, id#).',
        nargs=2,
        default=False,
        metavar=('Type', 'ID')
    )

    # Run Application.delete_template().
    parser.add_argument(
        '-l',
        '--delete',
        help='Delete a specific note template. Args=(type, id#)',
        nargs=2,
        default=False,
        metavar=('Type', 'ID')
    )

    # Run Application.edit_template().
    parser.add_argument(
        '-e',
        '--edit',
        help="Edit specified note template. Args=(id, type, 'note'). Id is immutable and must exist. Type and note will"
             " change to input. note must be surrounded by quotation marks: ''."
             "will change to inputs.",
        nargs=3,
        default=False,
        metavar=('ID', 'Type', 'Note')
    )

    args = parser.parse_args()  # Collect arguments.

    log.debug(f'args: {args}')
    log.debug('parse_args complete.')

    return args


def handle_args(args):
    """Handle args when parse_args() receives inputs.

    Args:
        args (List [args]): List of arguments from argument parser.

    Returns:
        None
    """

    log.debug('Checking for arguments from terminal...')

    # Check for arguments from arg_parse()
    run_args = False
    arguments = args.__dict__
    for k, v in arguments.items():
        if v is not False:
            run_args = True
            continue

    if run_args is False:  # When no arguments from arg_parse() run self_test()
        log.debug('No arguments from arg_parse. Running self_test()...')
        self_test()
        log.debug('self_test() complete.')

    log.debug('arg_parse() arguments found.')

    app = Application()
    log.debug('Parsing arguments through application...')

    if args.test:
        self_test()  # Test application.py
        storage_self_test()  # Test storage.py/

    # Run Application.today_date().
    if args.date:
        print(app.today_date())

    # Run Application.display_all_of_type().
    if args.all:
        print(app.display_all_of_type(args.all[0]))

    # Run Application.display_template().
    if args.display:
        print(app.display_template(args.display[0], args.display[1]))

    # Run Application.delete_template().
    if args.delete:
        result = app.delete_template(args.delete[0], args.delete[1])
        if result is True:
            print(f'Note template has been deleted. Type: {args.delete[0]}, ID: {args.delete[1]}.')
        else:
            print(f'Note template could not be deleted. Type: {args.delete[0]}, ID: {args.delete[1]}.')

    # Run Application.edit_template().
    if args.edit:
        arg = {
            'id': int(args.edit[0]),
            '_type': args.edit[1],
            'note': args.edit[2]
        }

        result = app.edit_template(arg)
        if result is None:
            print('Note template has NOT been modified!')
        else:
            print(f'{result} has been modified.')

    return app


def self_test():
    """Run Unittests on module.

        Runs when application.py is called directly. Creates a new yaml file with random records for testing. Conducts
        testing with Unittest, and deletes test file when complete.

    Args:
        None

    Returns:
        None
    """

    import os
    import unittest

    import test_application
    from test_application import create_random
    from test_application import APPLICATION_TESTING_RECORDS_FILENAME

    repo = Repo()

    # Create test file.
    records = create_random()
    test_file = open(APPLICATION_TESTING_RECORDS_FILENAME, 'w')
    repo._save_to_yaml(records, APPLICATION_TESTING_RECORDS_FILENAME)
    test_file.close()

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_application)
    unittest.TextTestRunner(verbosity=2).run(suite)

    # Delete test file upon completion.
    os.remove(APPLICATION_TESTING_RECORDS_FILENAME)


def test():
    """For development level module testing."""

    app = Application()
    pass


def main():

    # Configure logging.
    logging.basicConfig(
        level=DEFAULT_LOG_LEVEL,
        format=f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - %(message)s',
        filename=LOG_FILENAME,
    )

    log.debug('main...')

    app = handle_args(parse_args())  # Returns instance of application.

    app.save(app.templates)

    log.debug('main.')


if __name__ == '__main__':
    # self_test()
    # test()
    main()
