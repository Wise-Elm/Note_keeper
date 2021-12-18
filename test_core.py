#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module performs a unittest on core.py"""

import random
import unittest

from core import _Template  # ABC.

from test_assets import create_random_template


# Setup elements for testing.

class_names = [cls.__name__ for cls in _Template.__subclasses__()]
# Generate list of template subclasses.
#   Example:
#       class_names = ['Surgery', 'ComprehensiveExam', 'etc']

subclass_obj = _Template.__subclasses__()
# Generate list of template subclass objects.
#   Example:
#       subclass_obj = [<class 'core.LimitedExam'>, <class 'core.Surgery'>, <class 'core.HygieneExam'>, etc.]


subclasses = dict(zip(class_names, subclass_obj))
# Generate dictionary of template class names as keys and objects as values.
#   Example:
#       self.subclasses = {
#           'LimitedExam': <class 'core.LimitedExam'>,
#           'Surgery': <class 'core.Surgery'>,
#           'HygieneExam': <class 'core.HygieneExam'>,
#           'PeriodicExam': <class 'core.PeriodicExam'>,
#           'ComprehensiveExam': <class 'core.ComprehensiveExam'>
#       }


# Randomly choose instance attributes to instantiate.

choice = random.choice(class_names)  # Choose class type.

template = create_random_template(type_=choice)
# Dictionary of randomly chosen attributes for chosen class type.
#   Example:
#       template = {
#           '_type': 'Surgery,
#           'id': 0123456789,
#           'note': 'This is a note.'
#       }

test_class = subclasses[choice]  # Identify child class object.
instance = test_class(template)  # Instantiate instance.

instance_dict = instance.to_dict()  # to_dict() used on object used to make sure it is instantiated correctly.
#   Example:
#       instance_dict = {
#           '_type': 'Surgery,
#           'id': 0123456789,
#           'note': 'This is a note.'
#       }


class TestCore(unittest.TestCase):
    """Perform unittest of core.py."""

    def test_child_classes(self):
        """Test instantiation of _Template child classes."""

        self.assertIsInstance(instance, test_class)

    def test_ABC(self):
        """Test instantiation of _Template (ABC)."""

        self.assertIsInstance(instance, _Template)

    def test__repr__(self):
        """Test _Template __repr__."""

        msg = f"{instance_dict['_type']}, id: {instance_dict['id']}"
        self.assertEqual(instance.__repr__(), msg)

    def test__str__(self):
        """Test _Template __str__."""

        msg = f"Type: {instance_dict['_type']}\nID: {instance_dict['id']}\n\n{instance_dict['note']}"
        self.assertEqual(instance.__str__(), msg)

    def test_to_dict(self):
        """Test _Template to_dict."""

        self.assertEqual(template, instance.to_dict())
