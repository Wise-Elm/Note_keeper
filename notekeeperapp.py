#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'


"""Note organization application.

-This program is currently in production, and is primarily derived for the purpose of learning Python.-

This application is designed to aid in writing medical notes by allowing the user to construct, save, display, delete, 
and edit note templates. Note templates are intended to provide the basic structure of a patient note so that the 
practitioner can save time by filling the details rather than constructing a completely new note.
"""

# Todo (GS): Configure a rotating log handler.

import argparse
from datetime import date
import logging
from random import randint
import sys

# Todo (GS): Possibly change ID_DIGIT_LENGTH to a range, ex: ID_RANGE = (x, y)
from core import core_self_test, ID_DIGIT_LENGTH, RUNTIME_ID

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
        #       self.subclasses = {
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
            new.note = original.note

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


def persistent():  # TODO (GS): run_application(). should be a method within the application, which gets passed the args object.
    """Run application in persistent mode.

    Allows user friendly interaction with program from shell.

    Args:
        None

    Returns:
        None
    """

    log.debug('Program being run in persistent mode...')

    app = NoteKeeperApp()

    # Introduction graphic formatting.
    graphic_space = 9
    graphic_indent = 8

    print('Welcome to:')  # TODO (GS): method print_welcome()
    print(f"{' ' * graphic_indent}         __  _____  __{' ' * graphic_space}      __   __   __   __   __   ")
    print(f"{' ' * graphic_indent} /\  /  /  \   |   |__{' ' * graphic_space}|_/  |__  |__  |_/  |__  |__|  ")
    print(f"{' ' * graphic_indent}/  \/   \__/   |   |__{' ' * graphic_space}| \  |__  |__  |    |__  |  \  ")
    print('\n')
    print("Application is being run in persistent mode. Enter 'menu' for a list of options, or 'quit' to exit.")

    # Menu display formatting.
    menu_space = 20
    menu_indent = 4
    # TODO (GS): method print_menu(). Argument determins if returns print or returns string. method get_welcome, and method print_welcome.
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
    while run is True:  # TODO (GS): while is running. Called main event loop. put into method main_event_loop that gets called if args calls for persistent method.

        arg = input('\nEnter your selection: ')  # TODO (GS): change arg to user_input.

        if arg.lower() == 'menu' or arg.lower() == 'help' or arg.lower() == 'h':  # TODO (GS): leave out 'h'.
            print(menu)
            continue
        # TODO (GS): if users input is in map, call corresponding function, else: syntax error.
        elif arg.lower() == 'add' or arg.lower() == 'a':  # TODO (GS): make each block a function since they are each little work pieces.
            print(f'Available types: {[k for k in app.note_classes.keys()]}.')  # Generate list of note class names.
            type_ = input('Enter note type: ')
            note = input('Enter note: ')
            try:
                result = app.create_note({'_type': type_, 'note': note})
                print(f'New note template:\n\n{result}\n')
                print('Note template has been added.')
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'date' or arg.lower() == 'da':
            print(f"Today's date: {date.today()} (yyyy-mm-dd).")
            continue

        elif arg.lower() == 'delete' or arg.lower() == 'de':
            print(f'Available types: {[k for k in app.note_classes.keys()]}.')  # Generate list of note class names.
            id_ = input('Id to delete: ')
            try:
                print(app.delete_note(id_))
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'display' or arg.lower() == 'd':
            id_ = input('Enter template id: ')
            try:
                print(app.get_note(id_).__str__())
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'display type' or arg.lower() == 'dt':
            print(f'Available types: {[k for k in app.note_classes.keys()]}.')  # Generate list of note class names.
            type_ = input('Enter template type: ')
            try:
                text = ''
                num = 0
                for note in app.templates[type_]:
                    num += 1
                    out_str = f'\n\nNumber: {num}\n' + note.__str__() + '\n'
                    text += out_str

                if len(text) == 0:
                    text = f'No notes found for type: {type_}'

                return text

            except StorageError as se:
                print(se)
                continue

        elif arg.lower() == 'edit' or arg.lower() == 'e':
            print(f'Available types: {[k for k in app.note_classes.keys()]}.')  # Generate list of note class names.
            type_ = input('Type to edit: ')
            id_ = int(input('Id to edit: '))
            print('Enter key will input the note.')
            note = input('Enter new note: \n')
            argument = {'_type': type_, 'id': id_, 'note': note}
            try:
                app.edit_note(argument)
                print(f'Note template has been edited.')
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'save' or arg.lower() == 's':
            try:
                app.save()
                print('Program Saved.')
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'quit' or arg.lower() == 'q':
            option = input('Would you like to save y/n?: ')
            if option.lower() == 'y':
                app.save()
                print('Program Saved.')
                run = False  # Quit while loop and end program.
                continue
            elif option.lower() != 'n':
                print('Invalid selection.')
            else:
                print('Program not saved.')
                run = False  # Quit while loop and end program.
                continue

        else:
            print('Invalid selection.')

    print('Good bye!')

    log.debug('Persistent mode has ended.')

    return


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
        persistent()

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
    # TODO (GS): sys.exit(0) from module level.
