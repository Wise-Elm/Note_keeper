#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module is used to test notekeeperapp.py"""

import random
import unittest

from notekeeper import NoteKeeper

from core import _Template

from test_assets import create_random_id
from test_assets import create_random_note
from test_assets import create_random_templates
from test_assets import create_random_type


# Setup instance for testing.
app = NoteKeeper()
# TODO (GS): core.get_notes.
app.templates = {cls.__name__: [] for cls in _Template.__subclasses__()}  # Reset app.templates to unloaded format.
#   Example:
#       app.templates = {
#           'LimitedExam': [],
#           'Surgery': [],
#           'HygieneExam': [],
#           'PeriodicExam': [],
#           'ComprehensiveExam': []
#       }
# TODO (GS): be able to tell app what file to open, for a list of note classes, request new note when i give it a type.
app = create_random_templates(app=app)  # Create random test data and add to instance.
#   Uses create_random_templates() from test_assets to return the same instance of app as in the argument, but with
#   app.templates populated with test data.
#   Example:
#       app.templates = {
#           'LimitedExam': [LimitedExam objects],
#           'Surgery': [Surgery objects],
#           'HygieneExam': [HygieneExam objects],
#           'PeriodicExam': [PeriodicExam objects],
#           'ComprehensiveExam': [ComprehensiveExam objects]
#       }
# TODO (GS): app.get_note_classes.
# Since app was instantiated upon testing, point repo.templates at new templates.
app.repo.templates = app.templates

# Repopulate repo.ids with current ids.
ids = []
for class_name, notes in app.repo.templates.items():
    for note in notes:
        ids.append(note.id)
app.repo.ids = ids
# TODO (GS): unittest testcase should be a setup and teardown.


class TestApplication(unittest.TestCase):
    """Test application.py."""

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_create_note(self):
        """Test Application.create_note().

        Asserts that the template object is added correctly be checking the length of the template object list for the
        corresponding template type before and after it is added, and asserts that the template is instantiated into the
        correct object parent and child classes.
        """

        cls_names = [k for k in app.note_classes.keys()]  # Generate list of note class names.

        random_note = {# TODO (GS): change to mock note.
            '_type': create_random_type(cls_names),
            'id': create_random_id(app),
            'note': create_random_note()# TODO (GS): create_mock_comments().
        }

        len_before = len(app.templates[random_note['_type']])
        new_template_obj = app.create_note(random_note)# TODO (GS): note rather than new_template_obj
        app.repo.ids.append(new_template_obj.id)  # Add id to repo.ids to prevent error when testing delete.# TODO (GS):  dont directly communite with repo.
        len_after = len(app.templates[random_note['_type']])
        # TODO (GS):  just use app.get_note()
        self.assertEqual(len_before+1, len_after)
        self.assertIsInstance(new_template_obj, app.note_classes[random_note['_type']])
        self.assertIsInstance(new_template_obj, _Template)

    def test_delete_note(self):
        """Test Application.delete_note().

        Picks a random note template from instance, asserts the existence of template, deletes template, and asserts the
        non existence to template. After testing, adds template object back into instance.
        """
        # TODO (GS):  Just ask app for note classes back as a list.
        cls_names = [k for k in app.note_classes.keys()]  # Generate list of note class names.
        test_template = random.choice(cls_names)
        test_template = random.choice(app.templates[test_template])

        # Confirm that note is included in program.
        self.assertIn(test_template, app.templates[test_template.__class__.__name__])

        first_len = len(app.templates[test_template.__class__.__name__])

        app.delete_note(test_template.id)

        # Confirm object has been removed.
        self.assertNotIn(test_template, app.templates[test_template.__class__.__name__])
        # Confirm that the list the object was in is now one shorter.
        self.assertEqual(first_len, len(app.templates[test_template.__class__.__name__]) + 1)

        # Add template back to prevent testing problems that arise from other unitest methods checking for the original
        # testing data.
        app.create_note(test_template.to_dict())

    def test_get_note(self):
        """Test Application.get_note().

        Assert Application.get_note() returns the correct note.
        """
        # TODO (GS): get rid of random in all of this.
        cls_names = [k for k in app.note_classes.keys()]  # Generate list of note class names.
        random_name = random.choice(cls_names)
        random_obj = random.choice(app.templates[random_name])
        first_template = random_obj
        second_template = app.get_note(random_obj.id)

        self.assertIs(first_template, second_template)
        # TODO (GS): create a mode that will test all the way to disc.
    def test_edit_note(self):
        """Test Application.edit_note().

        Tests that objects are edited properly by editing a template and confirming the proper changes are made.
        """
        cls_names = [k for k in app.note_classes.keys()]
        _type = random.choice(cls_names) # TODO (GS): Should be type_, with _ after the name.
        pick = random.choice(app.templates[_type])

        modified_template = {
            '_type': _type,
            'id': pick.id,
            'note': 'This is a test'
        }
        # TODO (GS): app should have method that returns the individual note classes, not the names.
        result = app.edit_note(modified_template)

        # Confirm accuracy of edited note template.
        self.assertDictEqual(modified_template, result.to_dict())

        # Find original edited template.
        for template in app.templates[_type]:
            if template.id == modified_template['id']:
                new_template = template

        # Confirm edited note template was added to Application.template correctly.
        self.assertDictEqual(modified_template, new_template.to_dict())


if __name__ == '__main__':
    unittest.main()
