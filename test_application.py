#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module is used to test application.py"""

import random
import unittest

from notekeeperapp import NoteKeeperApp

from core import _Template

from test_assets import create_random_id
from test_assets import create_random_note
from test_assets import create_random_templates
from test_assets import create_random_type


# Setup instance for testing.
app = NoteKeeperApp()

app.templates = {cls.__name__: [] for cls in _Template.__subclasses__()}  # Reset app.templates to unloaded format.
#   Example:
#       app.templates = {
#           'LimitedExam': [],
#           'Surgery': [],
#           'HygieneExam': [],
#           'PeriodicExam': [],
#           'ComprehensiveExam': []
#       }

app = create_random_templates(app=app)  # Create random test data and add to instance.
#   Example:
#       app.templates = {
#           'LimitedExam': [LimitedExam objects],
#           'Surgery': [Surgery objects],
#           'HygieneExam': [HygieneExam objects],
#           'PeriodicExam': [PeriodicExam objects],
#           'ComprehensiveExam': [ComprehensiveExam objects]
#       }

# Since app was instantiated upon testing, point repo.templates at new templates.
app.repo.templates = app.templates


class TestApplication(unittest.TestCase):
    """Test application.py."""

    def test_add_template(self):
        """Test Application.add_template().

        Asserts that the template object is added correctly be checking the length of the template object list for the
        corresponding template type before and after it is added, and asserts that the template is instantiated into the
        correct object parent and child classes.
        """

        cls_names = [k for k in app.note_classes.keys()]  # Generate list of note class names.

        random_note = {
            '_type': create_random_type(cls_names),
            'id': create_random_id(app),
            'note': create_random_note()
        }

        len_before = len(app.templates[random_note['_type']])
        new_template_obj = app.create_note(random_note)
        len_after = len(app.templates[random_note['_type']])

        self.assertEqual(len_before+1, len_after)
        self.assertIsInstance(new_template_obj, app.note_classes[random_note['_type']])
        self.assertIsInstance(new_template_obj, _Template)

    def test_get_note(self):
        """Test Application.get_note().

        Assert Application.get_note() returns the correct note.
        """

        cls_names = [k for k in app.note_classes.keys()]  # Generate list of note class names.
        random_name = random.choice(cls_names)
        random_obj = random.choice(app.templates[random_name])
        first_template = random_obj
        second_template = app.get_note(random_obj.id)

        self.assertIs(first_template, second_template)

    def test_delete_template(self):
        """Test Application.delete_template().

        Picks a random note template from instance, asserts the existence of template, deletes template, and asserts the
        non existence to template. After testing, adds template object back into instance.
        """

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

        # Add template back to prevent testing problems that arise from other unitests checking for the original testing
        # data.
        app.create_note(test_template.to_dict())

    def test_edit_template(self):
        """Test Application.edit_template().

        Tests that objects are edited properly by editing a template and confirming the proper changes are made.
        """
        cls_names = [k for k in app.note_classes.keys()]
        _type = random.choice(cls_names)
        pick = random.choice(app.templates[_type])

        modified_template = {
            '_type': _type,
            'id': pick.id,
            'note': 'This is a test'
        }

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
