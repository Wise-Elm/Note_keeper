#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module is used to test application.py"""

import random
import unittest

from application import Application

from core import _Template

from test_assets import create_random_id
from test_assets import create_random_note
from test_assets import create_random_templates
from test_assets import create_random_type


# Setup instance for testing.
app = Application()

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


class TestApplication(unittest.TestCase):
    """Test application.py."""

    def test_add_template(self):
        """Test Application.add_template().

        Asserts that the template object is added correctly be checking the length of the template object list for the
        corresponding template type before and after it is added, and asserts that the template is instantiated into the
        correct object parent and child classes.
        """

        subclasses = app.subclass_names

        random_note = {
            '_type': create_random_type(subclasses),
            'id': create_random_id(app),
            'note': create_random_note()
        }

        len_before = len(app.templates[random_note['_type']])
        new_template_obj = app.add_template(random_note)
        len_after = len(app.templates[random_note['_type']])

        self.assertEqual(len_before+1, len_after)
        self.assertIsInstance(new_template_obj, app.subclasses[random_note['_type']])
        self.assertIsInstance(new_template_obj, _Template)

    def test_display_template(self):
        """Test Application.display_template().

        Assert that template objects are displayed correctly by using app.display_template to generate one
        representation, and comparing that against another representation derived from template objects __str__()
        method.
        """

        random_name = random.choice(app.subclass_names)
        random_obj = random.choice(app.templates[random_name])
        first_template = random_obj.__str__()
        second_template = app.display_template(random_obj.to_dict()['_type'], random_obj.id)

        self.assertEqual(first_template, second_template)

    def test_delete_template(self):
        """Test Application.delete_template().

        Picks a random note template from instance, asserts the existence of template, deletes template, and asserts the
        non existence to template. After testing, adds template object back into instance.
        """

        test_template = random.choice(app.subclass_names)
        test_template = random.choice(app.templates[test_template])

        # Confirm length of list before object is removed.
        self.assertIn(test_template, app.templates[test_template.__class__.__name__])

        first_len = len(app.templates[test_template.__class__.__name__])
        app.delete_template(test_template.__class__.__name__, test_template.id)

        # Confirm object has been removed.
        self.assertNotIn(test_template, app.templates[test_template.__class__.__name__])
        # Confirm that the list the object was in is now one shorter.
        self.assertEqual(first_len, len(app.templates[test_template.__class__.__name__]) + 1)

        # Add template back to prevent testing problems that arise from other unitests checking for the original testing
        # data.
        app.add_template(test_template.to_dict())

    def test_edit_template(self):
        """Test Application.edit_template().

        Tests that objects are edited properly by editing a template and confirming the proper changes are made.
        """

        _type = random.choice(app.subclass_names)
        pick = random.choice(app.templates[_type])

        modified_template = {
            '_type': _type,
            'id': pick.id,
            'note': 'This is a test'
        }

        result = app.edit_template(modified_template)

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
