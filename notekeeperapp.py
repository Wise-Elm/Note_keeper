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

from core import ID_DIGIT_LENGTH  # Todo (GS): either core.ID_DIGIT_LENGTH or import ID_DIGIT_LENGTH, RUNTIME_IT, ... coudl be ID_RANGE = (x, y)
from core import RUNTIME_ID
from core import core_self_test

from storage import Repo
from storage import storage_self_test


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

        self.subclass_names = self.repo.subclass_names  # List of valid template classes.  # Todo (GS): drop class names because ther are already in self.subclasses.
        #   Example:  # Todo (GS): when call to self.subclass_names it should just be a calculation of self.subclasses.
        #       self.subclass_names = ['Surgery', 'ComprehensiveExam', 'etc']

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

        Returns:
            note (_Template): New note.
        """

        log.debug('Creating new note...')

        # Check if new_template can be associated with a valid class.
        if new_template['_type'] not in self.subclass_names:
            msg = 'Note Template type: {}, not allowed.'.format(new_template['_type'])
            log.warning(msg)
            raise NoteKeeperApplicationError(msg)

        # If id_ is None generate a new unique id.
        if id_ is None:
            id_ = self._generate_random_id()

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

    def _generate_random_id(self):  # TODO (GS):  could give the note class itself the ability to generate id numbers if needed.
        """Generate a unique id.

        Args:
            None

        Returns:
            id_ (int): A unique id number of the proper length (ID_DIGIT_LENGTH).  # TODO (GS):  ids should be strings.
        """
        # TODO (GS): classic way is to just generate a uuid module. uuid.uid4(). could use just first 5 digits, check if unique.
        log.debug('Generate new id number...')

        is_unique = False
        is_long_enough = False
        while not is_unique or not is_long_enough:
            id_ = randint(int('1' + ('0' * (ID_DIGIT_LENGTH - 1))), int('9' * ID_DIGIT_LENGTH))  # TODO (GS): just use randint(min, max)
            #   Example if ID_DIGIT_LEN == 3:
            #       id_ = int between 100 & 999.

            if len(str(id_)) == ID_DIGIT_LENGTH:  # TODO (GS):  could check it number is less than min.
                is_long_enough = True

            if id_ not in self.ids:
                is_unique = True

            if id_ is False or is_unique is False:
                id_, is_unique = False, False

        log.debug('New id number generated.')

        return id_

    def display_template(self, type_, id_):  # TODO (GS): should not be called display. to_pretty_note, or something lol
        """Display a note template.  # TODO (GS): redundant.
      # TODO (GS): replace display_template with get_note. just return note. Call repo to get note.
        Args:
            type_ (str): Template class type. ex: 'Surgery'.
            id_ (str OR int): id number for desired template.

        Returns:
            template (str): Note template matching the id number and type_ from arguments.
        """

        log.debug('Finding template to display...')

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

        if type_ not in self.templates:  # Check legality of type_.
            msg = 'Entered type is not valid.'
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

        for template in self.templates[type_]:
            if template.id == id_:
                msg = 'Template found.'
                log.debug(msg)
                return template.__str__()

        # When template not found.
        msg = f'Template with type: {type_}, id: {type_} NOT found.'
        log.debug(msg)
        raise NoteKeeperApplicationError(msg)

    def display_all_of_type(self, type_):  # TODO (GS): junk function. whatever calls this should concatinate the notes.
        """Displays all note templates from specified type.

        Concatenates all from type together as one long string in the form of an easily readable text document.

        Args:
            type_ (str): Type of note template. ex: 'Surgery'.

        Returns:
            text (str): Formatted string containing all note templates from argument type.
        """

        log.debug('Compiling display data...')

        if type_ not in self.templates:  # Check legality of _type.
            msg = f'Entered type: ({type_}), is not valid.'
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

        text = ''
        num = 0
        for template in self.templates[type_]:
            num += 1
            out_str = f'\n\nNumber: {num}\n' + template.__str__() + '\n'
            text += out_str

        log.debug('Display data compiled.')

        if len(text) == 0:  # When type_ is valid but no records exist.
            text = f'No templates of type: {type_} found.'

        log.debug('Display data compiled.')

        return text

    def delete_template(self, type_, id_):  # TODO (GS): delete_note. get ride of argument(type_).
        """Delete note template.
        # TODO (GS): should just tell repo to delete. should be a delete method in repo.
        Args:
            type_ (str): Template type. ex: 'Surgery'.
            id_ (int OR str): id number for note template to delete.

        Returns:
            (Bool): True if successful.
        """
        # TODO (GS): be aware that old numbers should be tracked.
        log.debug(f'Deleting template. Type: {type_}, id: {id_}...')

        if type(id_) is str:  # Check legality of id_.
            if not id_.isnumeric():
                msg = f'Entered id: ({id_}), is not valid. Must only contain numbers.'
                log.debug(msg)
                raise NoteKeeperApplicationError(msg)
            else:
                id_ = int(id_)

        if not type(id_) is int:  # Check legality of id_ argument.
            msg = 'Entered id is not valid. Must be all numbers.'
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

        if type_ not in self.templates:  # Check legality of type_.
            msg = 'Entered type is not valid.'
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

        for template in self.templates[type_]:
            if template.id == id_:
                index = self.templates[type_].index(template)  # Identify index of template to delete.
                self.templates[type_].pop(index)  # Remove template.
                msg = f'Template Type: {type_}, id: {id_}, has been deleted.'
                log.debug(msg)
                return True

        msg = f'Template Type: {type_}, id: {id_}, cannot be found and has NOT been deleted.'
        log.debug(msg)
        raise NoteKeeperApplicationError(msg)

    def edit_note(self, edited_template):
        """Edit note template attributes.

        Allows editing of note template attributes with exception of the id.

        Args:
            edited_template (dict): Dictionary of note template attributes.

        Returns:
            result (_NoteTemplate[obj]): Template object.
        """
        # TODO (GS): a note object should be editable. Get repo to change object type and return object. then user edits objects attributes.
        log.debug('Editing note template...')
        # TODO (GS): repo manages life cycle of objects. manufacture of id should probably be done in the repo.
        if type(edited_template['id']) is str:  # Check legality of id key.
            if not edited_template['id'].isnumeric():
                msg = f"Entered id: {edited_template['id']}, is not valid. Must be all numbers."
                log.debug(msg)
                raise NoteKeeperApplicationError(msg)
            else:
                edited_template['id'] = int(edited_template['id'])

        if not type(edited_template['id']) is int:  # Check legality of id key.
            msg = 'Entered id is not valid. Must be all numbers.'
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

        if edited_template['_type'] not in self.templates:  # Check legality of type_.
            msg = f"Entered type: {edited_template['_type']}, is not valid."
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

        if not type(edited_template['_type']) is str:  # Check legality of type_.
            msg = f"Entered type: {edited_template['_type']}, is not valid."
            log.debug(msg)
            raise NoteKeeperApplicationError(msg)

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
            raise NoteKeeperApplicationError(msg)

        # Delete original template. Delete is used rather than changing origional template attributes because templates
        # may be of a different object class.
        self.delete_template(original_template.to_dict()['_type'], original_template.id)

        # Add new template.
        result = self.create_note(new_template=edited_template, id_=edited_template['id'])
        msg = 'Note template has been edited.'
        log.debug(msg)

        log.debug('Editing note template complete.')

        return result

    def save(self, templates):  # TODO (GS): templates should not be an argument because it already know its own templates.
        """Save application data.  # TODO (GS): Remove argument from function.
        # TODO (GS): object already know the templates.
        Args:
            templates (dict): Keys=template class names, Values=[note templates].
                Example:
                    templates = {
                        'LimitedExam': [LimitedExam objects],
                        'Surgery': [Surgery objects],
                        'HygieneExam': [HygieneExam objects],
                        'PeriodicExam': [PeriodicExam objects],
                        'ComprehensiveExam': [ComprehensiveExam objects]
                    }

        Returns:
            None
        """

        log.debug('Saving...')

        if self.repo.save(templates):  # TODO (GS): just self.repo.save()
            log.debug('Saved.')
        else:
            msg = 'Error while attempting to save. Data not saved.'  # TODO (GS): should say where it was trying to save.
            log.critical(msg)
            raise NoteKeeperApplicationError(msg)  # TODO (GS): Let repo do the crashing. this error will suppress the repo error.

        log.debug('Saving complete.')


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
            print(f'Available types: {app.subclass_names}.')
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
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Type to delete: ')
            id_ = input('Id to delete: ')
            try:
                print(app.delete_template(type_, id_))
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'display' or arg.lower() == 'd':
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Enter template type: ')
            id_ = input('Enter template id: ')
            try:
                print(app.display_template(type_, id_))
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'display type' or arg.lower() == 'dt':
            print(f'Available types: {app.subclass_names}.')
            type_ = input('Enter template type: ')
            try:
                print(app.display_all_of_type(type_))
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'edit' or arg.lower() == 'e':
            print(f'Available types: {app.subclass_names}.')
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
                app.save(app.templates)
                print('Program Saved.')
                continue
            except NoteKeeperApplicationError as ae:
                print(ae)
                continue

        elif arg.lower() == 'quit' or arg.lower() == 'q':
            option = input('Would you like to save y/n?: ')
            if option.lower() == 'y':
                app.save(app.templates)
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
        description='This application is designed to aid in writing medical notes by allowing the user to construct, '
                    'save, display, delete, and edit note templates. Note templates are intended to provide the basic '
                    'structure of a patient note so that the practitioner can save time by filling the details rather '
                    'than constructing a completely new note.'
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

    # Run Application.display_all_of_type().
    parser.add_argument(
        '-a',
        '--all',
        help='Display all note templates of a type. Available note types: PeriodicExam, HygieneExam, Surgery, '
             'ComprehensiveExam, LimitedExam.',
        nargs=1,
        default=False,
        metavar='Type',
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
        nargs=2,
        default=False,
        metavar=('Type', 'ID')
    )

    # Run Application.delete_template().
    parser.add_argument(
        '-l',
        '--delete',
        help='Delete a specific note template.',
        nargs=2,
        default=False,
        metavar=('Type', 'ID')
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
            app.save(app.templates)
        except NoteKeeperApplicationError as ae:
            print(ae)

    # Run Application.display_all_of_type().
    if args.all:
        try:
            print(app.display_all_of_type(args.all[0]))
        except NoteKeeperApplicationError as ae:
            print(ae)

    # Run Application.display_template().
    if args.display:
        try:
            print(app.display_template(args.display[0], args.display[1]))
        except NoteKeeperApplicationError as ae:
            print(ae)

    # Run Application.delete_template().
    if args.delete:
        try:
            result = app.delete_template(args.delete[0], args.delete[1])
            if result is True:
                print('Note template has been deleted.')
                app.save(app.templates)
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
            app.save(app.templates)
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
