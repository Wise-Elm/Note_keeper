#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

"""Note organization application.

Context:
    This program is currently in production, and is primarily derived for the purpose of
     learning Python.
    
Description:
    This application is designed to aid in writing medical notes by allowing the user 
    to construct, save, display, delete, and edit note templates. Note templates are 
    intended to provide the basic structure of a patient note so that the practitioner 
    can save time by filling the details rather than constructing a completely new note.

Attributes:
    DEFAULT_LOG_FILENAME (str): Default file path for application wide logging.
    DEFAULT_LOG_LEVEL (:obj: 'int'): Integer represents a value which assigns a log 
        level from logging.
        
Composition Attributes:
    Line length = 88 Characters
"""


import argparse
import logging
import sys
from datetime import date
from logging import handlers

from core import CoreError, core_self_test, RUNTIME_ID, _Template
from storage import Repo, storage_self_test, StorageError


DEFAULT_LOG_FILENAME = 'note_keeper_log.log'
DEFAULT_LOG_LEVEL = logging.DEBUG

# Configure logging.
log = logging.getLogger()
log.addHandler(logging.NullHandler())


class NoteKeeperApplicationError(RuntimeError):
    """Base class for exceptions arising from this module."""


class NoteKeeper:
    """Handle interaction between program modules."""

    def __init__(self, test_=False, load=True):
        """Initializing NoteKeeper.

        Args:
            test_ (Bool, OPTIONAL): First parameter. Default is False. False signifies
                the application is not running a test, and thus should load the regular
                program data. True has application load mock data to perform unittest.
            load (Bool, OPTIONAL): Second parameter. Defaults to True. True signifies
                the application should load stored data. No data is loaded when
                load=False.

        Returns:
            None
        """

        log.debug('Starting Note Keeper...')

        self.repo = Repo()

        # Test argument load.
        if load is True:
            if test_ is True:
                self.repo.load_test()  # Load mock data for testing.
            else:
                self.repo.load()  # Load patient notes.

        # Dictionary: Keys=template class names, Values=[note templates].
        self.templates = self.repo.templates
        #   Example:
        #       self.templates = {
        #           'LimitedExam': [LimitedExam objects],
        #           'Surgery': [Surgery objects],
        #           'HygieneExam': [HygieneExam objects],
        #           'PeriodicExam': [PeriodicExam objects],
        #           'ComprehensiveExam': [ComprehensiveExam objects]
        #       }

        self.ids = self.repo.ids  # List storing template id's for each note template.

        # Dict: keys = class names, values = class objects.
        self.note_classes = self.repo.note_classes
        #   Example:
        #       self.note_classes = {
        #           'LimitedExam': <class 'core.LimitedExam'>,
        #           'Surgery': <class 'core.Surgery'>,
        #           'HygieneExam': <class 'core.HygieneExam'>,
        #           'PeriodicExam': <class 'core.PeriodicExam'>,
        #           'ComprehensiveExam': <class 'core.ComprehensiveExam'>
        #       }

        # Welcome message to display on program startup.
        self.welcome_message = self._get_welcome(return_str=True)

        # Map of program methods that are intended for use during main_event_loop().
        # Keys = inputs, Values = functions.
        self.options = {
            'add': self._get_add,
            'date': self.get_date,
            'delete': self._get_delete,
            'display': self._get_display,
            'display type': self._get_display_type,
            'edit': self._get_edit,
            'menu': self._get_menu,
            'save': self._get_save,
            'quit': self._get_quit,
            'workday': self.is_workday
        }

        log.debug('Note Keeper has started.')

    def create_note(self, new_template=None, id_=None, blank=False):
        """Create new note.

        Will create a new note with supplied argument data, or return a 'blank' note
        with attributes yet to be filled.

        When blank is True other arguments will be ignored.

        Args:
            new_template (dict, OPTIONAL): First parameter. Dictionary representation
                of a note. The id key/value is optional.
                Example:
                    new_template = {
                        '_type': 'Surgery,
                        'id': 0123456789, (OPTIONAL Key/Value)
                        'note': 'This is an example'
                    }

            id_ (int, OPTIONAL): Second parameter. Used to assign specific id number to
                new note if desired.

            blank (Bool, OPTIONAL): Third parameter. When True method will generate a
                note with an id, _Template as type, and an empty string as note.
                Example:
                      type(note) = _Template
                      note.id = randomly generated integer that complies with id
                        requirements.
                      note.note = '' (empty string)

        Returns:
            note (_Template): New note.
        """

        log.debug('Creating new note...')

        # User wants a note without a designated subclass of _Template, and a randomly
        # generated id.
        if blank is True:
            note_template = {'id': self.generate_id(), 'note': ''}
            note = _Template(note_template)
            return note

        else:  # User wants a note with a designated subclass of _Template.
            # Check if new_template can be associated with a valid class.
            # Generate list of note class names.
            cls_names = [k for k in self.note_classes.keys()]
            if new_template['_type'] not in cls_names:
                msg = f"Note Template type: {new_template['_type']}, not allowed."
                log.warning(msg)
                raise NoteKeeperApplicationError(msg)

            # If id_ is None generate a new unique id.
            if id_ is None:
                id_ = self.generate_id()

            note_template = {
                'id': id_,
                'note': new_template['note']
            }

            # Select appropriate object class for new note.
            cls = self.note_classes[new_template['_type']]
            note = cls(note_template)  # Instantiate note object.

            # Add new object to appropriate dictionary value in self.templates.
            self.templates[cls.__name__].append(note)

            log.debug('New note created and added.')

            return note

    def create_from_attributes(self, type_, notes, id_=None):
        """Helper method for create_note().

        Takes arguments and converts them to a dictionary representation of a note,
        then uses create_note() to return a note.

        Args:
            type_ (str): First parameter. A subclass of _Templates.
            notes (str): Second parameter.
            id_ (int, OPTIONAL): Third parameter. A note id. None will generate a
                randomized id.

        Returns:
            note
        """

        template = {'_type': type_, 'note': notes}
        note = self.create_note(new_template=template, id_=id_)
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

        note = self.repo.get_note(id_)

        return note

    def get_notes_of_type(self, type_, str_=False):
        """Return all notes of type in argument.

        Args:
            type_ (str): First parameter. Note Type.
            str_ (Bool): Second parameter. When True return is a string containing all
                notes of type in a nicely readable format.

        Returns:
            text (str): When str is True. String containing all notes of type in a
                nicely readable format.
            notes (lst): When str is False. All notes of argument type.
        """

        notes = self.repo.get_notes_of_type(type_)

        # When True present notes in pretty format.
        if str_ is True:
            text = ''
            num = 0
            notes = [note.__str__() for note in notes]
            for note in notes:
                num += 1
                pretty = f'\n\nNumber: {num}\n' + note + '\n'
                text += pretty
            return text

        return notes

    def delete_note(self, id_):
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
                msg = f"Entered id: {edited_template['id']}, is not valid. Must be " \
                      f"all numbers."
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
        # If note type is not going to change.
        if edited_template['_type'] == original.to_dict()['_type']:
            original.note = edited_template['note']
            new = original
        else:
            # Change note type.
            new = self.repo.edit_type(
                # Note on which to change.
                self.repo.get_note(edited_template['id']),
                # Desired _Template subclass.
                self.note_classes[edited_template['_type']]
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

    def get_class(self, note):
        """Get class object.

        Args:
            note (_Template): Note

        Returns:
            cls (_Template): Corresponding child class of _Template.
        """

        template = note.to_dict()
        cls = self.note_classes[template['_type']]

        return cls

    def main_event_loop(self):
        """Run application.

        Provides a user friendly interaction with program from shell. Program stay
        running until user quits.

        Args:
            None

        Returns:
            None
        """

        print(self.welcome_message)  # Print welcome message to screen.

        log.debug('Entering Main Event Loop...')

        run = True
        while run is True:
            result = self._get_user_inputs()
            if result is False:
                run = False

        log.debug('Main Event Loop has ended.')

        return

    def _get_user_inputs(self):
        """Prompts user for initial selection, then passes selection to appropriate
        methods.

        Args:
            None

        Returns:
            (False OR None): Returns to _main_event_loop(), False to end program, OR
                None to continue loop.
        """

        log.debug('Prompting user.')

        user_input = input('\nEnter your selection: ')

        log.debug(f'User selection: {user_input}.')

        if user_input.lower() in self.options:  # Check if user input is legal.
            result = self.options[user_input.lower()]()
            if result is False:  # Quit main_event_loop and end program.
                return False
            else:
                return True
        else:
            self._get_invalid()  # Handle indecipherable input.
            return True

    def _get_add(self):
        """Add new note.

        Prompts user for note attributes and adds new note based on inputs.

        Args:
            None

        Returns:
            None
        """

        # Generate list of note class names.
        print(f'Available types: {[k for k in self.note_classes.keys()]}.')
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

    @staticmethod
    def get_date(as_str=False):
        """Display current date.

        Args:
            as_str (bool, OPTIONAL): When True returns string, else prints to screen.

        Returns:
            result (str, OPTIONAL): Return string representation of date when as_str is
                True, prints to screen otherwise.
        """

        result = date.today()
        if result is None:
            msg = f'An error occurred while retrieving the date.'
            raise NoteKeeperApplicationError(msg)
        elif as_str is True:
            return result
        else:
            print(f"Today's date: {result}")

    @staticmethod
    def is_workday(date_=None):
        """Determines if a date is a regular workday: Monday-Friday.

        Args:
            date_ (str, OPTIONAL): String representation of a date using the format
                yyyy-mm-dd. Defaults to prompting user for date.

        Returns:
            (Bool): True if workday (Monday-Friday), False otherwise (Saturday or
                Sunday).
        """

        if date_ is None:
            date_ = input('Enter a date (yyyy-mm-dd): ')
            y, m, d = date_.split('-')

        else:
            y, m, d = date_.split('-')

        try:
            # Within the datetime module days to the week are represented by the
            # integers 0-6, with Monday being 0.
            if date(int(y), int(m), int(d)).weekday() < 5:
                print(f'{date_} is a regular workday.')
                return
            else:
                print(f'{date_} is not a regular workday.')

        except ValueError as ve:
            print(ve)
            return

    def _get_delete(self):
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

    def _get_display(self):
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

    def _get_display_type(self):
        """Displays all notes of a type.

        Prompts user for note type and displays all notes of that type.

        Args:
            None

        Returns:
            None
        """

        # Generate list of note class names.
        print(f'Available types: {[k for k in self.note_classes.keys()]}.')
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

    def _get_edit(self):
        """Allows user to edit the attributes of a note, including type, and note
        content.

        Prompts user for note id, finds associated note, and prompts user for new
        attributes for associated note.

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

    def _get_save(self):
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

    def _get_quit(self):
        """Quit application.

        Prompts user to save application before ending program, performs save if
        requested, then returns False to end the Main Event Loop.

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

    def _get_invalid(self):
        """Signifies to user when prompts entered during _parse_user_inputs() are
        invalid.

        Args:
            None

        Returns:
            None
        """

        print('Invalid input.')
        return

    def _get_welcome(self, return_str=False):
        """Display a welcome message and graphic, OR return a string representation of
        the welcome message.

        Args:
            return_str (bool): Defaults to False, and prints to screen. When true,
                returns the welcome as a string.

        Returns:
            welcome (str): Returns welcome when return_str is True.
        """

        log.debug('Getting welcome...')

        # Welcome graphic formatting.
        graphic_space = 9
        graphic_indent = 8

        welcome = (
            f"Welcome to:\n" 
            f"{' ' * graphic_indent}         __  _____  __"
            f"{' ' * graphic_space}      __   __   __   __   __   \n" 
            f"{' ' * graphic_indent} /\  /  /  \   |   |__"
            f"{' ' * graphic_space}|_/  |__  |__  |_/  |__  |__|  \n" 
            f"{' ' * graphic_indent}/  \/   \__/   |   |__"
            f"{' ' * graphic_space}| \  |__  |__  |    |__  |  \  \n\n" 
            "Application is being run in persistent mode. Enter 'menu' for a list of "
            "options, or 'quit' to exit."
        )

        if return_str is True:
            log.debug('Returning welcome as string.')
            return welcome

        else:
            log.debug('Printing welcome to screen.')
            print(welcome)

    def _get_menu(self, return_str=False):
        """Display an options menu, OR return a string representation of the options
        menu.

        Args:
            return_str (bool): Defaults to False, and prints to screen. When true,
                returns the menu as a string.

        Returns:
            menu (str): Returns menu when return_str is True.
        """

        log.debug('Getting menu...')

        # Menu display formatting.
        menu_space = 20
        menu_indent = 4

        menu = (
            f"Optional inputs:\n" 
            f"{' ' * menu_indent}add{' ' * (menu_space - len('add'))} "
            f"Add a new note template.\n" 
            f"{' ' * menu_indent}date{' ' * (menu_space - len('date'))} "
            f"Display today's date\n" 
            f"{' ' * menu_indent}workday{' ' * (menu_space - len('workday'))} "
            f"Signify if date is a workday.\n" 
            f"{' ' * menu_indent}delete{' ' * (menu_space - len('delete'))} "
            f"Delete a note template.\n" 
            f"{' ' * menu_indent}display{' ' * (menu_space - len('display'))} "
            f"Display note template.\n" 
            f"{' ' * menu_indent}display type{' ' * (menu_space - len('display type'))} "
            f"Display all note templates of a type.\n" 
            f"{' ' * menu_indent}edit{' ' * (menu_space - len('edit'))} "
            f"Edit a note template.\n" 
            f"{' ' * menu_indent}save{' ' * (menu_space - len('save'))} "
            f"Option to save changes.\n" 
            f"{' ' * menu_indent}quit{' ' * (menu_space - len('quit'))} "
            f"Quit Program."
        )
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
        description='Welcome to Note Keeper. This application is designed to aid in '
                    'writing medical notes by allowing the user to construct, save, '
                    'display, delete, and edit note templates. Note templates are '
                    'intended to provide the basic structure of a patient note so that '
                    'the practitioner can save time by filling the details rather than '
                    'constructing a completely new note.',
        epilog='When no arguments are present application will run from shell in '
               'persistent mode.'
    )

    # Run Application.self_test().
    parser.add_argument(
        '-t',
        '--test',
        help='Run testing on application to confirm program is running correctly and '
             'exit. OK = Pass.',
        action='store_true',
        default=False
    )

    # Run Application._get_date().
    parser.add_argument(
        '-d',
        '--date',
        help="Return today's date and exit.",
        action='store_true',
        default=False
    )

    # Run Application.is_workday().
    parser.add_argument(
        '-wd',
        '--workday',
        help="Signify if input date is a workday. Entry should be in format: "
             "yyyy-mm-dd.",
        nargs=1,
        default=False,
        metavar='Date'
    )

    # Concatenate notes of argument type using Application.get_note().
    parser.add_argument(
        '-a',
        '--all',
        help='Display all notes of a type. Available note types: PeriodicExam, '
             'HygieneExam, Surgery, =ComprehensiveExam, LimitedExam.',
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
        help="Edit a note template. Args=(id, type, 'note'). Id is immutable and must "
             "exist. Type and note will= change to input. Note must be surrounded by "
             "quotation marks.",
        nargs=3,
        default=False,
        metavar=('ID', 'Type', 'Note')
    )

    args = parser.parse_args()  # Collect arguments.

    log.debug(f'args: {args}')
    log.debug('parse_args complete.')

    return args


def run_application(args):
    """Run application based on shell commands.

    Args:
        args (List [args]): List of arguments from argument parser.

    Returns:
        None
    """

    log.debug('Checking for arguments from shell...')

    if args.test:
        log.debug('Begin unittests on notekeeper.py, storage.py, and core.py...')

        self_test()  # Test application.py
        storage_self_test()  # Test storage.py
        core_self_test()  # Test core.py
        return

    app = NoteKeeper()  # Begin application instance.
    log.debug('NoteKeeper instantiated.')

    if args.add:
        note = app.create_from_attributes(type_=args.add[0], notes=args.add[1])
        print(f'Note: {note}, has been created.')
        return

    elif args.date:
        print(app.get_date())
        return

    elif args.workday:
        print(app.is_workday(args.workday[0]))
        return

    elif args.all:
        print(app.get_notes_of_type(args.all[0], str_=True))
        return

    elif args.display:
        print(app.get_note(args.display[0]).__str__())
        return

    elif args.delete:
        app.delete_note(args.delete_note[0])
        return

    elif args.edit:
        app.edit_note(edited_template={
            'id': args.edit[0],
            'type_': args.edit[1],
            'note': args.edit[2]
        })
        return

    else:
        app.main_event_loop()
        return


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

    print(type(logging.DEBUG))


def main():

    # Configure Rotating Log.
    handler = handlers.RotatingFileHandler(
        filename=DEFAULT_LOG_FILENAME,
        maxBytes=100**3,
        backupCount=1)
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(DEFAULT_LOG_LEVEL)

    log.debug('main...')

    args = parse_args()
    run_application(args)  # Returns instance of application.

    log.debug('main.')

    sys.exit(0)


if __name__ == '__main__':
    main()
