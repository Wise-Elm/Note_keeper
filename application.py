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

from core import _Template
from core import ID_DIGIT_LENGTH
from core import RUNTIME_ID


from storage import Repo
from storage import storage_self_test


LOG_FILENAME = 'application.log'
DEFAULT_LOG_LEVEL = logging.DEBUG

# Configure logging.
log = logging.getLogger(__name__)
log.setLevel(DEFAULT_LOG_LEVEL)


# TODO (GS): ApplicationError
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
        self.subclass_names = self.repo.subclass_names
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
            msg = 'Note Template type not allowed.'
            log.critical(msg)
            raise ApplicationError(msg)

        # Format new_template Keys and values for inclusion into self.templates.
        if _id is None:
            _id = self._generate_random_id()

        output_template = {
            'id': _id,
            'note': new_template['note']
        }

        subclass_obj = _Template.__subclasses__()  # Generate list of template class objects.
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
            msg (str): Message indicating the success or failure of the function.
        """

        log.debug('Finding template to display...')

        if type(_id) is str:  # Check legality of _id.
            if not _id.isnumeric():
                msg = 'Entered id is not valid. Must be all numbers.'
                log.debug(msg)
                raise ApplicationError(msg)
            else:
                _id = int(_id)

        if _type not in self.templates:  # Check legality of _type.
            msg = 'Entered type is not valid.'
            log.debug(msg)
            raise ApplicationError(msg)

        for template in self.templates[_type]:
            if template.id == _id:
                msg = 'Template found.'
                log.debug(msg)
                return template.__str__(), msg

        # When template not found.
        msg = f'Template with type: {_type}, id: {_type} NOT found.'
        log.debug(msg)

        return None, msg

    def display_all_of_type(self, _type):
        """Displays all note templates from specified type.

        Concatenates all from type together as one long string in the form of a text document.

        Args:
            _type (str): Type of note template.

        Returns:
            long_text (str): Formatted string containing all note templates from argument type.
        """

        log.debug('Compiling display data...')

        if _type not in self.templates:  # Check legality of _type.
            msg = 'Entered type is not valid.'
            log.debug(msg)
            raise ApplicationError(msg)

        long_text = ''
        num = 1
        for template in self.templates[_type]:
            out_str = f'\n\nNumber: {num}\n' + template.__str__() + '\n'
            long_text += out_str
            num += 1

        log.debug('Display data compiled.')

        return long_text

    def delete_template(self, _type, _id):
        """Delete note template.

        Args:
            _type (str): Template type.
            _id (int OR str): id number for note template to delete.

        Returns:
            result (Bool): True if successful, False otherwise.
            msg (str): Message indicating the success or failure of function.
        """

        log.debug(f'Deleting template. Type: {_type}, id: {_id}...')

        if type(_id) is str:  # Check legality of _id.
            if not _id.isnumeric():
                msg = 'Entered id is not valid. Must be all numbers.'
                log.debug(msg)
                raise ApplicationError(msg)
            else:
                _id = int(_id)

        if _type not in self.templates:  # Check legality of _type.
            msg = 'Entered type is not valid.'
            log.debug(msg)
            raise ApplicationError(msg)

        for template in self.templates[_type]:
            if template.id == _id:
                _index = self.templates[_type].index(template)
                self.templates[_type].pop(_index)
                msg = f'Template Type: {_type}, id: {_id}, has been deleted.'
                log.debug(msg)
                return True, msg

        msg = f'Template Type: {_type}, id: {_id}, cannot be found and has NOT been deleted.'
        log.debug(msg)
        return False, msg

    def edit_template(self, edited_template):
        """Edit note template attributes.

        Edit all attributes of a note template except the id number.

        Args:
            edited_template (dict): Dictionary of note template attributes.

        Returns:
            result (_NoteTemplate[obj] OR None): Object if successful, None otherwise.
        """

        log.debug('Editing note template...')

        if type(edited_template['id']) is str:  # Check legality of id key.
            if not edited_template['id'].isnumeric():
                msg = 'Entered id is not valid. Must be all numbers.'
                log.debug(msg)
                raise ApplicationError(msg)
            else:
                edited_template['id'] = int(edited_template['id'])

        if edited_template['_type'] not in self.templates:  # Check legality of _type.
            msg = 'Entered type is not valid.'
            log.debug(msg)
            raise ApplicationError(msg)

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
            msg = 'Edit failed! Template not found for ID: {}.'.format(edited_template['id'])
            log.debug(msg)
            raise ApplicationError(msg)

        # Delete original template.
        self.delete_template(original_template.to_dict()['_type'], original_template.id)

        # Add new template.
        result = self.add_template(new_template=edited_template, _id=edited_template['id'])
        msg = 'Note template has been edited.'
        log.debug(msg)

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


def persistent():
    """Run application in persistent mode.

    Args:
        None

    Returns:
        None
    """

    # TODO (GS): add logging.

    app = Application()

    graphic_space = 9
    graphic_indent = 8

    print('Welcome to:')
    print(f"{' ' * graphic_indent}         __  _____  __{' ' * graphic_space}      __   __   __   __   __   ")
    print(f"{' ' * graphic_indent} /\  /  /  \   |   |__{' ' * graphic_space}|_/  |__  |__  |_/  |__  |__|  ")
    print(f"{' ' * graphic_indent}/  \/   \__/   |   |__{' ' * graphic_space}| \  |__  |__  |    |__  |  \  ")
    print('\n')
    print("Application is being run in persistent mode. Enter 'menu' for a list of options, or 'quit' to exit.")

    menu_space = 20
    menu_indent = 4

    menu = f"Optional inputs:\n" \
           f"{' ' * menu_indent}add OR a{' ' * (menu_space - len('add OR a'))} Add a new note template.\n" \
           f"{' ' * menu_indent}date OR da{' ' * (menu_space - len('date OR da'))} Display today's date\n" \
           f"{' ' * menu_indent}delete OR de{' ' * (menu_space - len('delete OR de'))} Delete a note template.\n" \
           f"{' ' * menu_indent}display OR d{' ' * (menu_space - len('display OR d'))} Display note template.\n" \
           f"{' ' * menu_indent}display type OR dt{' ' * (menu_space - len('display type OR dt'))} Display all note " \
           f"templates of a type.\n" \
           f"{' ' * menu_indent}edit OR e{' ' * (menu_space - len('edit OR e'))} Edit a note template.\n" \
           f"{' ' * menu_indent}save OR s{' ' * (menu_space - len('save OR s'))} Option to save changes.\n" \
           f"{' ' * menu_indent}quit OR q{' ' * (menu_space - len('quit OR q'))} Quit Program."

    run = True
    while run is True:

        arg = input('\nEnter your selection: ')

        if arg.lower() == 'menu' or arg.lower() == 'help' or arg.lower() == 'h':
            print(menu)

        elif arg.lower() == 'add' or arg.lower() == 'a':
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Enter note type: ')
            note = input('Enter note: ')
            try:
                result = app.add_template({'_type': type_, 'note': note})
                print(f'New note template:\n\n{result}\n')
                print('Note template has been added.')
            except ApplicationError as AE:
                print(AE)

        elif arg.lower() == 'date' or arg.lower() == 'da':
            print(f"Today's date: {app.today_date()} (yyyy-mm-dd).")

        elif arg.lower() == 'delete' or arg.lower() == 'de':
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Type to delete: ')
            id_ = input('Id to delete: ')
            try:
                result = app.delete_template(type_, id_)
                if result[0] is True:
                    print(result[1])
                else:
                    print(result[1])
            except ApplicationError as AE:
                print(AE)

        elif arg.lower() == 'display' or arg.lower() == 'd':
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Enter template type: ')
            id_ = input('Enter template id: ')
            try:
                result = app.display_template(type_, id_)
                if result[0] is None:
                    print(result[1])
                else:
                    print(f'{result[1]}\n\n{result[0]}')
            except ApplicationError as AE:
                print(AE)

        elif arg.lower() == 'display type' or arg.lower() == 'dt':
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Enter template type: ')
            try:
                print(app.display_all_of_type(type_))
            except ApplicationError as AE:
                print(AE)

        elif arg.lower() == 'edit' or arg.lower() == 'e':
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Type to edit: ')
            id_ = int(input('Id to edit: '))
            print('Enter key will input the note. To move to a new line rather than hitting enter type "\ n", without'
                  ' the space.')
            note = input('Enter new note: \n')
            argument = {'_type': type_, 'id': id_, 'note': note}
            try:
                result = app.edit_template(argument)
                print(f'{result} has been edited.')
            except ApplicationError as AE:
                print(AE)

        elif arg.lower() == 'save' or arg.lower() == 's':
            app.save(app.templates)
            print('Program Saved.')

        elif arg.lower() == 'quit' or arg.lower() == 'q':
            option = input('Would you like to save y/n?: ')
            if option.lower() == 'y':
                app.save(app.templates)
                print('Program Saved.')
                run = False  # Quit while loop and end program.
            elif option.lower() != 'n':
                print('Invalid selection.')
            else:
                print('Program not saved.')
                run = False  # Quit while loop and end program.

        else:
            print('Invalid selection.')

    print('Good bye!')
    return


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
        help='Display all note templates for argument type. Available note types: PeriodicExam, HygieneExam, Surgery, '
             'ComprehensiveExam, LimitedExam.',
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

    # TODO (GS): develop this argument.
    # Run Application in persistent mode through terminal.
    parser.add_argument(
        '-p',
        '--persistent',
        help='Run application in persistent mode through the terminal.',
        default=False,
        action='store_true'
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

    if args.test:  # TODO (GS): Problem with this.
        self_test()  # Test application.py
        storage_self_test()  # Test storage.py/

    app = Application()
    log.debug('Parsing arguments through application...')

    # Run Application.today_date().
    if args.date:
        print(app.today_date())

    # Run Application.display_all_of_type().
    if args.all:
        result = app.display_all_of_type(args.all[0])
        if len(result) == 0:
            print('No templates of that type found.')
        else:
            print(result)

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

    if args.persistent:
        persistent()

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

    import unittest

    import test_application

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_application)
    unittest.TextTestRunner(verbosity=2).run(suite)


def test():
    """For development level module testing."""

    pass


def main():

    # TODO (GS): Add rotating logging.
    # Configure logging.
    logging.basicConfig(
        level=DEFAULT_LOG_LEVEL,
        format=f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - %(message)s',
        filename=LOG_FILENAME,
    )

    log.debug('main...')

    handle_args(parse_args())  # Returns instance of application.

    log.debug('main.')


if __name__ == '__main__':
    # self_test()
    # test()
    main()
