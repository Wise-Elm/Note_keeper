#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

import copy

"""Note organization application.

-This program is currently in production, and is primarily derived for the purpose of learning Python.-

This application is designed to aid in writing medical notes by allowing the user to construct, save, display, delete, 
and edit note templates. Note templates are intended to provide the basic structure of a patient note so that the 
practitioner can save time by filling the details rather than constructing a completely new note.
"""

# TODO (GS): Configure a rotating log handler.

import argparse
from datetime import date
import logging
import sys

from core import CoreError, core_self_test, RUNTIME_ID

from storage import Repo, storage_self_test, StorageError


DEFAULT_LOG_FILENAME = 'note_keeper_log.log'
DEFAULT_LOG_LEVEL = logging.DEBUG

# Configure logging.
log = logging.getLogger()
log.addHandler(logging.NullHandler())


class NoteKeeperApplicationError(RuntimeError):
    """Base class for exceptions arising from this module."""


class NoteKeeperApp:
    """Handle interaction between program modules."""

    def __init__(self):

        log.debug('Starting Note Keeper...')

        self.repo = Repo()
        self.repo.load()  # Automatically load data.

        self.templates = self.repo.templates  # Dictionary: Keys=template class names, Values=[note templates].
        #   Example:
        #       self.templates = {
        #           'LimitedExam': [LimitedExam objects],
        #           'Surgery': [Surgery objects],
        #           'HygieneExam': [HygieneExam objects],
        #           'PeriodicExam': [PeriodicExam objects],
        #           'ComprehensiveExam': [ComprehensiveExam objects]
        #       }

        self.ids = self.repo.ids  # List storing template id's for each note template.

        self.note_classes = self.repo.note_classes  # Dict: keys = class names, values = class objects.
        #   Example:
        #       self.note_classes = {
        #           'LimitedExam': <class 'core.LimitedExam'>,
        #           'Surgery': <class 'core.Surgery'>,
        #           'HygieneExam': <class 'core.HygieneExam'>,
        #           'PeriodicExam': <class 'core.PeriodicExam'>,
        #           'ComprehensiveExam': <class 'core.ComprehensiveExam'>
        #       }

        log.debug('Note Keeper has started.')

    def create_note(self, new_template, id_=None):
        """Add new note.

        Args:
            new_template (dict): Dictionary representation of a note. The id key/value is optional.
                Example:
                    new_template = {
                        '_type': 'Surgery,
                        'id': 0123456789, (OPTIONAL Key/Value)
                        'note': 'This is an example'
                    }

            id_ (int, OPTIONAL): Used to assign specific id number to new note note if desired.

        Returns:  # TODO (GS): Change all Returns to Return?
            note (_Template): New note.
        """

        log.debug('Creating new note...')

        # Check if new_template can be associated with a valid class.
        cls_names = [k for k in self.note_classes.keys()]  # Generate list of note class names.
        if new_template['_type'] not in cls_names:
            msg = 'Note Template type: {}, not allowed.'.format(new_template['_type'])
            log.warning(msg)
            raise NoteKeeperApplicationError(msg)

        # If id_ is None generate a new unique id.
        if id_ is None:
            id_ = self.generate_id()

        note_template = {
            'id': id_,
            'note': new_template['note']
        }

        cls = self.note_classes[new_template['_type']]  # Select appropriate object class for new note.
        note = cls(note_template)  # Instantiate note object.

        # Add new object to appropriate dictionary value in self.templates.
        self.templates[cls.__name__].append(note)

        log.debug('New note created and added.')

        return note

    def generate_id(self):
        """Generate a unique id.

        Args:
            None

        Returns:
            id_ (int): A unique id number of the proper length (ID_DIGIT_LENGTH).
        """

        id_ = self.repo.generate_id()

        return id_

    def get_note(self, id_):
        """Return a note displayed in a nice readable format.

        Args:
            id_ (str OR int): id number for desired template.

        Returns:
            note (_Template): Returns the note with a id that matches argument.
        """

        log.debug('Finding note...')

        if type(id_) is str:  # Check legality of id_ argument.
            if not id_.isnumeric():
                msg = 'Entered id is not valid. Must be all numbers.'
                log.debug(msg)
                raise NoteKeeperApplicationError(msg)
            else:
                id_ = int(id_)

        if not type(id_) is int:  # Check legality of id_ argument.
            msg = 'Entered id is not valid. Must be all numbers.'
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

        note = self.repo.get_note(id_)

        log.debug('Note found, returning note.')

        return note

    def delete_note(self, id_):  # TODO (GS): Develop way to track deleted ids.
        """Delete note.

        Uses Repo.delete_note() to remove note from program.

        Args:
            id_ (int OR str): id number for note template to delete.

        Returns:
            (Bool): True if successful.
        """

        result = self.repo.delete_note(id_)
        return result

    def edit_note(self, edited_template):
        """Edit note template attributes.

        Allows editing of note template attributes with exception of the id.

        Args:
            edited_template (dict): Dictionary of note template attributes.

        Returns:
            result (_NoteTemplate[obj]): Template object.
        """

        log.debug('Editing note template...')

        if type(edited_template['id']) is str:  # Check legality of id key.
            if not edited_template['id'].isnumeric():
                msg = f"Entered id: {edited_template['id']}, is not valid. Must be all numbers."
                log.warning(msg)
                raise NoteKeeperApplicationError(msg)
            else:
                edited_template['id'] = int(edited_template['id'])

        if not type(edited_template['id']) is int:  # Check legality of id key.
            msg = 'Entered id is not valid. Must be all numbers.'
            log.warning(msg)
            raise NoteKeeperApplicationError(msg)

        if edited_template['_type'] not in self.templates:  # Check legality of _type.
            msg = f"Entered type: {edited_template['_type']}, is not valid."
            log.warning(msg)
            raise NoteKeeperApplicationError(msg)

        if not type(edited_template['_type']) is str:  # Check legality of _type.
            msg = f"Entered type: {edited_template['_type']}, is not valid."
            log.warning(msg)
            raise NoteKeeperApplicationError(msg)

        original = self.repo.get_note(edited_template['id'])  # Find note to edit.

        # Check type.
        if edited_template['_type'] == original.to_dict()['_type']:  # If note type is not going to change.
            original.note = edited_template['note']
            new = original
        else:
            # Change note type.
            new = self.repo.edit_type(
                self.repo.get_note(edited_template['id']),  # Note on which to change.
                self.note_classes[edited_template['_type']]  # Desired _Template subclass.
                )
            new.note = edited_template['note']

        msg = 'Note has been edited.'
        log.debug(msg)

        return new  # Return resultant note.

    def save(self):
        """Save application data.

        Args:
            None

        Returns:
            None
        """

        log.debug('Saving...')

        result = self.repo.save()

        log.debug('Saving complete.')

        return result

    def run_application(self):
        """Run application in persistent mode.

        Provides a user friendly interaction with program from shell. Program stay running until user quits.

        Args:
            None

        Returns:
            None
        """

        log.debug('Program being run in persistent mode...')

        self._get_welcome()  # Print welcome message.
        self._main_event_loop()

        log.debug('Persistent mode has ended.')

    def _main_event_loop(self):
        """Main event loop for program.

        Args:
            None

        Returns:
            None
        """

        log.debug('Entering Main Event Loop...')

        run = True
        while run is True:
            result = self._parse_user_inputs()
            if result is False:
                run = False

        log.debug('Main Event Log has ended.')

        return

    def _parse_user_inputs(self):
        """Prompts user if initial selection, then passes selection to appropriate methods.

        Args:
            None

        Returns:
            (False OR None): Returns to _main_event_loop(), False to end program, OR None to continue loop.
        """

        log.debug('Prompting user.')

        user_input = input('\nEnter your selection: ')

        log.debug(f'User selection: {user_input}.')

        # Keys = inputs, Values = functions.
        options = {
            'add': self._user_add,
            'date': self._user_date,
            'delete': self._user_delete,
            'display': self._user_display,
            'display type': self._user_display_type,
            'edit': self._user_edit,
            'menu': self._get_menu,
            'save': self._user_save,
            'quit': self._user_quit
        }

        if user_input.lower() in options:  # Check if user input is legal.
            result = options[user_input]()
            if result is False:  # Quit main_event_loop and end program.
                return False
            else:
                return
        else:
            self._user_invalid()  # Handle indecipherable input.

    def _user_add(self):
        """Add new note.

        Prompts user for note attributes and adds new note based on inputs.

        Args:
            None

        Returns:
            None
        """

        print(f'Available types: {[k for k in self.note_classes.keys()]}.')  # Generate list of note class names.
        type_ = input('Enter note type: ')
        note = input('Enter note: ')
        try:
            result = self.create_note({'_type': type_, 'note': note})
            print(f'New note template:\n\n{result}\n')
            print('Note template has been added.')
        except CoreError as ce:
            print(ce)
        except NoteKeeperApplicationError as ae:
            print(ae)
        except StorageError as se:
            print(se)
        finally:
            return

    def _user_date(self):
        """Display current date.

        Args:
            None

        Returns:
            None
        """

        result = date.today()
        if result is None:
            msg = f'An error occurred while retrieving the date.'
            raise NoteKeeperApplicationError(msg)
        else:
            print(f"Today's date: {result}")

    def _user_delete(self):
        """Delete note.

        Prompts user for note id and deletes associated note.

        Args:
            None

        Returns:
            None
        """

        id_ = input('Id of note to delete: ')
        try:
            print(self.delete_note(id_))
        except CoreError as ce:
            print(ce)
        except NoteKeeperApplicationError as ae:
            print(ae)
        except StorageError as se:
            print(se)
        finally:
            return

    def _user_display(self):
        """Displays a note.

        Prompts user for note id and displays associated note.

        Args:
            None

        Returns:
            None
        """

        id_ = input('Enter template id: ')
        try:
            print(self.get_note(id_).__str__())
        except CoreError as ce:
            print(ce)
        except NoteKeeperApplicationError as ae:
            print(ae)
        except StorageError as se:
            print(se)
        finally:
            return

    def _user_display_type(self):
        """Displays all notes of a type.

        Prompts user for note type and displays all notes of that type.

        Args:
            None

        Returns:
            None
        """

        print(f'Available types: {[k for k in self.note_classes.keys()]}.')  # Generate list of note class names.
        print('Entry is case sensitive.')
        type_ = input('Enter template type: ')
        try:
            text = ''
            num = 0
            for note in self.templates[type_]:
                num += 1
                out_str = f'\n\nNumber: {num}\n' + note.__str__() + '\n'
                text += out_str

            if len(text) == 0:
                text = f'No notes found for type: {type_}'

            print(text)

        except CoreError as ce:
            print(ce)
        except NoteKeeperApplicationError as ae:
            print(ae)
        except StorageError as se:
            print(se)
        finally:
            return

    def _user_edit(self):
        """Allows user to edit the attributes of a note, including type, and note content.

        Prompts user for note id, finds associated note, and prompts user for new attributes for associated note.

        Args:
            None

        Returns:
            None
        """

        # Determine id of note to edit.
        try:
            id_ = int(input('Enter id of note to edit: '))
        except ValueError:
            print('Input id must be an integer.')
            return

        # Display note when found.
        try:
            print('\n' + self.get_note(id_).__str__() + '\n')
        except CoreError as ce:
            print(ce)
            return
        except NoteKeeperApplicationError as ae:
            print(ae)
            return
        except StorageError as se:
            print(se)
            return

        # Prompt user for new attributes.
        print('You are allowed to edit the type and note content.')
        type_ = input('Enter type for note: ')
        note = input('Enter new note content. Pressing Enter will input the note: \n')
        argument = {'_type': type_, 'id': id_, 'note': note}

        # Change attributes of associated note.
        try:
            new = self.edit_note(argument)
            msg = f"Note template has been edited:\n{new.__str__()}"
            print(msg)
        except CoreError as ce:
            print(ce)
        except NoteKeeperApplicationError as ae:
            print(ae)
        except StorageError as se:
            print(se)
        finally:
            return

    def _user_save(self):
        """Save application data.

        Args:
            None

        Returns:
            None
        """

        try:
            self.save()
            print('Data saved.')
        except CoreError as ce:
            print(ce)
        except NoteKeeperApplicationError as ae:
            print(ae)
        except StorageError as se:
            print(se)
        finally:
            return

    def _user_quit(self):
        """Quit application.

        Prompts user to save application before ending program, performs save if requested, then returns False to end
        the Main Event Loop.

        Args:
            None

        Returns:
            None
        """

        option = input('Would you like to save y/n?: ')
        if option.lower() == 'y':
            self.save()
            print('Program Saved.')
            return False  # Quit main_event_loop and end program.
        elif option.lower() != 'n':
            print('Invalid selection.')
            return
        else:
            print('Program not saved.')
            return False  # Quit main_event_loop and end program.

    def _user_invalid(self):
        """Signifies to user when prompts entered during _parse_user_inputs() are invalid.

        Args:
            None

        Returns:
            None
        """

        print('Invalid input.')
        self._parse_user_inputs()

    def _get_welcome(self, return_str=False):
        """Display a welcome message and graphic, OR return a string representation of the welcome message.

        Args:
            return_str (bool): Defaults to False, and prints to screen. When true, returns the welcome as a string.

        Returns:
            welcome (str): Returns welcome when return_str is True.
        """

        log.debug('Getting welcome...')

        # Welcome graphic formatting.
        graphic_space = 9
        graphic_indent = 8

        welcome = f"Welcome to:\n" \
            f"{' ' * graphic_indent}         __  _____  __{' ' * graphic_space}      __   __   __   __   __   \n" \
            f"{' ' * graphic_indent} /\  /  /  \   |   |__{' ' * graphic_space}|_/  |__  |__  |_/  |__  |__|  \n" \
            f"{' ' * graphic_indent}/  \/   \__/   |   |__{' ' * graphic_space}| \  |__  |__  |    |__  |  \  \n\n" \
            "Application is being run in persistent mode. Enter 'menu' for a list of options, or 'quit' to exit."

        if return_str is True:
            log.debug('Returning welcome as string.')
            return welcome

        else:
            log.debug('Printing welcome to screen.')
            print(welcome)

    def _get_menu(self, return_str=False):
        """Display an options menu, OR return a string representation of the options menu.

        Args:
            return_str (bool): Defaults to False, and prints to screen. When true, returns the menu as a string.

        Returns:
            menu (str): Returns menu when return_str is True.
        """

        log.debug('Getting menu...')

        # Menu display formatting.
        menu_space = 20
        menu_indent = 4

        menu = f"Optional inputs:\n" \
               f"{' ' * menu_indent}add{' ' * (menu_space - len('add'))} Add a new note template.\n" \
               f"{' ' * menu_indent}date{' ' * (menu_space - len('date'))} Display today's date\n" \
               f"{' ' * menu_indent}delete{' ' * (menu_space - len('delete'))} Delete a note template.\n" \
               f"{' ' * menu_indent}display{' ' * (menu_space - len('display'))} Display note template.\n" \
               f"{' ' * menu_indent}display type{' ' * (menu_space - len('display type'))} Display all note " \
               f"templates of a type.\n" \
               f"{' ' * menu_indent}edit{' ' * (menu_space - len('edit'))} Edit a note template.\n" \
               f"{' ' * menu_indent}save{' ' * (menu_space - len('save'))} Option to save changes.\n" \
               f"{' ' * menu_indent}quit{' ' * (menu_space - len('quit'))} Quit Program."

        if return_str is True:
            log.debug('Returning menu as string.')
            return menu

        else:
            log.debug('Printing menu to screen.')
            print(menu)


def parse_args(argv=sys.argv):
    """Setup shell environment to run program."""

    log.debug('parse_args...')

    # Program description.
    parser = argparse.ArgumentParser(
        description='Welcome to Note Keeper.',
        epilog='This application is designed to aid in writing medical notes by allowing the user to construct, save, '
               'display, delete, and edit note templates. Note templates are intended to provide the basic structure '
               'of a patient note so that the practitioner can save time by filling the details rather than '
               'constructing a completely new note.'
    )

    # TODO (GS): hand a help epilogue.
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
        help="Return today's date and exit.",
        action='store_true',
        default=False
    )

    # Concatenate notes of argument type using Application.get_note().
    parser.add_argument(
        '-a',
        '--all',
        help='Display all notes of a type. Available note types: PeriodicExam, HygieneExam, Surgery, '
             'ComprehensiveExam, LimitedExam.',
        nargs=1,
        default=False,
        metavar='Type'
    )

    # Run Application.add_template().
    parser.add_argument(
        '-x',
        '--add',
        help='Add a new note template. Note must be surrounded by quotation marks.',
        nargs=2,
        default=False,
        metavar=('Type', 'Note')
    )

    # Run Application.display_template().
    parser.add_argument(
        '-w',
        '--display',
        help='Display a specific note template.',
        nargs=1,
        default=False,
        metavar='ID'
    )

    # Run Application.delete_note().
    parser.add_argument(
        '-l',
        '--delete',
        help='Delete a note template.',
        nargs=1,
        default=False,
        metavar='ID'
    )

    # Run Application.edit_template().
    parser.add_argument(
        '-e',
        '--edit',
        help="Edit a note template. Args=(id, type, 'note'). Id is immutable and must exist. Type and note will"
             " change to input. Note must be surrounded by quotation marks.",
        nargs=3,
        default=False,
        metavar=('ID', 'Type', 'Note')
    )

    # Run Application in persistent mode through terminal.
    parser.add_argument(
        '-p',
        '--persistent',
        help='Run application in persistent mode through the terminal.',
        default=False,
        action='store_true'
    )
    # TODO (GS): if user --h will print help and exit program on line 644.
    args = parser.parse_args()  # Collect arguments.
    # TODO (GS): look up help eppilogue in argparse
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

    log.debug('Checking for arguments from shell...')

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

    if args.test:
        log.debug('Begin unittest...')

        self_test()  # Test application.py
        storage_self_test()  # Test storage.py
        core_self_test()  # Test core.py

        log.debug('Unittest complete.')

    app = NoteKeeperApp()
    log.debug('Parsing arguments through application...')

    # Run Application.today_date().
    if args.date:
        print(date.today())

    # Run Application.add_template().
    if args.add:
        arg = {
            '_type': args.add[0],
            'note': args.add[1]
        }
        try:
            result = app.create_note(arg)
            print(f"Note template Type: {result.to_dict()['_type']}, has been added.")
            app.save()
        except NoteKeeperApplicationError as ae:
            print(ae)

    # Concatenate notes of argument type using Application.get_note().
    if args.all:
        try:
            text = ''
            num = 0
            for note in app.templates[args.all[0]]:
                num += 1
                out_str = f'\n\nNumber: {num}\n' + note.__str__() + '\n'
                text += out_str

            if len(text) == 0:
                text = f'No notes found for type: {args.all[0]}'

            return text

        except StorageError as se:
            print(se)

    # Run Application.get_note().
    if args.display:
        try:
            print(app.get_note(args.display[0]).__str__())
        except NoteKeeperApplicationError as ae:
            print(ae)

    # Run Application.delete_template().
    if args.delete:
        try:
            result = app.delete_note(args.delete_note[0])
            if result is True:
                print('Note template has been deleted.')
                app.save()
        except NoteKeeperApplicationError as ae:
            print(ae)

    # Run Application.edit_template().
    if args.edit:
        arg = {
            'id': int(args.edit[0]),
            '_type': args.edit[1],
            'note': args.edit[2]
        }
        try:
            result = app.edit_note(arg)
            print(result.to_dict()['_type'] + ', id: ' + str(result.to_dict()['id']) + ', has been edited.')
            app.save()
        except NoteKeeperApplicationError as ae:
            print(ae)

    if args.persistent:
        app.run_application()
        # persistent()

    return app


def self_test():
    """Run Unittests on module.

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


def main():  # TODO (GS): main should start the application.

    # TODO (GS): Add rotating logging.
    # Configure logging.
    logging.basicConfig(
        level=DEFAULT_LOG_LEVEL,
        format=f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - %(message)s',
        filename=DEFAULT_LOG_FILENAME,
    )

    log.debug('main...')

    handle_args(parse_args())  # Returns instance of application.

    log.debug('main.')


if __name__ == '__main__':
    # self_test()
    # test()
    main()
    # TODO (GS): sys.exit(0) from module level.t
