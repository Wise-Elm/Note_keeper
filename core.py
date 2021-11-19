#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This module provides object classes for application.py."""

import logging
import unittest
import uuid

RUNTIME_ID = uuid.uuid4()  # Set unique id for each runtime.
ID_DIGIT_LENGTH = 10


class _NoteTemplate:
    """Objects of this type represent a periodontal appointment note template."""

    def __init__(self, template):
        self.note = template['note']  # type(str). Content of note template.
        self.id = template['id']  # type(int). Unique identification number for note template.
        """
        Args:
            template (dict): Note template.
            
        Returns:
            None
        """

    def __str__(self):
        return f'{self.__class__.__name__}, id: {self.id}'

    def __eq__(self, other):
        """Return true if other is deemed equal to this note template.

        Compares dictionary exam type and id with objects.

        Args:
            other (dict OR Obj): Dictionary representation of a note template OR a _NoteTemplate obj.

        Returns:
            is_equivalent (bool): True if equal, False otherwise.
        """

        if type(other) is self.__class__:
            if self.__class__.__name__ == other.__class__.__name__ and self.id == other.id:
                return True
            else:
                return False

        if self.__class__.__name__ == other['_type'] and self.id == other['id']:
            return True
        else:
            return False

    def to_dict(self):
        """Return a dictionary representation of _Note.

        Args:
            None

        Returns:
            note (dict): A dictionary of this object's attrs as keys, and their values.
        """

        note = self.__dict__
        note['_type'] = self.__class__.__name__

        return note

    def text_display(self):
        """Return a string formatted to display self. Return is an easy to read text representation.

        Args:
            None

        Returns:
            display_text (str): Attributes from self formatted into easy to read text.
        """

        template = self.to_dict()
        display_text = 'Type: {}\nID: {}\n\n{}'.format(template['_type'], template['id'], template['note'])
        return display_text


class Limited(_NoteTemplate):
    """Child class of _Note. Objects of this type represent a limited note template."""

    def __init__(self, template):
        """
        Args:
            template (dict): Note template.

        Returns:
            None
        """

        super().__init__(template)

    def to_dict(self):
        """Return a dictionary representation of Limited.

        Args:
            None

        Returns:
            note (dict): A dictionary of this object's attrs as keys, and their values.
        """

        note = super().to_dict()

        return note


class Surgery(_NoteTemplate):
    """Child class of _Note. Objects of this type represent a surgery note template."""

    def __init__(self, template):
        """
        Args:
            template (dict): Note template.

        Returns:
            None
        """

        super().__init__(template)

    def to_dict(self):
        """Return a dictionary representation of Surgery.

        Args:
            None

        Returns:
            note (dict): A dictionary of this object's attrs as keys, and their values.
        """

        note = super().to_dict()

        return note


class Hygiene(_NoteTemplate):
    """Child class of _Note. Objects of this type represent a hygiene note template."""

    def __init__(self, template):
        """
        Args:
            template (dict): Note template.

        Returns:
            None
        """

        super().__init__(template)

    def to_dict(self):
        """Return a dictionary representation of Hygiene.

        Args:
            None

        Returns:
            note (dict): A dictionary of this object's attrs as keys, and their values.
        """

        note = super().to_dict()

        return note


class Periodic(_NoteTemplate):
    """Child class of _Note. Objects of this type represent a periodic note template."""

    def __init__(self, template):
        """
        Args:
            template (dict): Note template.

        Returns:
            None
        """

        super().__init__(template)

    def to_dict(self):
        """Return a dictionary representation of Periodic.

        Args:
            None

        Returns:
            note (dict): A dictionary of this object's attrs as keys, and their values.
        """

        note = super().to_dict()

        return note


class Comprehensive(_NoteTemplate):
    """Child class of _Note. Objects of this type represent a comprehensive note template."""

    def __init__(self, template):
        """
        Args:
            template (dict): Note template.

        Returns:
            None
        """

        super().__init__(template)

    def to_dict(self):
        """Return a dictionary representation of Comprehensive.

        Args:
            None

        Returns:
            note (dict): A dictionary of this object's attrs as keys, and their values.
        """

        note = super().to_dict()

        return note
