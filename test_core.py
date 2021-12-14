#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module performs a unittest on core.py"""

import random
import unittest

from core import _Template  # ABC.

from test_assets import create_random_template

# Setup elements for testing.
class_names = [cls.__name__ for cls in _Template.__subclasses__()]  # Generate list of template subclasses.
subclass_obj = _Template.__subclasses__()  # Generate list of template subclass objects.
# Generate dictionary of template class names as keys and objects as values.
subclasses = dict(zip(class_names, subclass_obj))

# Randomly choose instance attributes in instantiate.
choice = random.choice(class_names)  # Choose class type.
template = create_random_template(type_=choice)  # Dictionary of randomly chosen attributes for chosen class type.
test_class = subclasses[choice]  # Identify child class object.
instance = test_class(template)  # Instantiate instance.

instance_dict = instance.to_dict()


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
