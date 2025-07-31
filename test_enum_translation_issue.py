#!/usr/bin/env python
"""
Test script to reproduce the enum translation issue described in the problem statement.
"""

import os
import sys
import enum

# Add Django to path
sys.path.insert(0, '/home/runner/work/django-django-11815/django-django-11815')

import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        USE_I18N=True,
        USE_L10N=True,
        USE_TZ=True,
    )

django.setup()

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.migrations.serializer import serializer_factory


class Status(enum.Enum):
    GOOD = _('Good')  # 'Good' will be translated
    BAD = _('Bad')    # 'Bad' will be translated

    def __str__(self):
        return self.name


def test_current_behavior():
    """Test the current enum serialization behavior."""
    print("Testing current enum serialization behavior:")
    
    # Test serializing Status.GOOD
    enum_value = Status.GOOD
    serializer = serializer_factory(enum_value)
    serialized, imports = serializer.serialize()
    
    print(f"Enum value: {enum_value}")
    print(f"Enum name: {enum_value.name}")
    print(f"Enum value.value: {enum_value.value}")
    print(f"Serialized: {serialized}")
    print(f"Imports: {imports}")
    
    # Try to reconstruct the enum using the serialized form
    print("\nTrying to execute the serialized code:")
    try:
        # This simulates what happens when Django loads an old migration
        exec_globals = {'__main__': __import__('__main__')}
        result = eval(serialized, exec_globals)
        print(f"Successfully reconstructed: {result}")
        print(f"Equal to original: {result == enum_value}")
    except Exception as e:
        print(f"ERROR: {e}")
        print("This demonstrates the issue - if the translation changes, old migration files break!")


def test_proposed_solution():
    """Test how the proposed solution would work."""
    print("\n" + "="*60)
    print("Testing proposed solution using enum name:")
    
    enum_value = Status.GOOD
    enum_class = enum_value.__class__
    module = enum_class.__module__
    
    # This is what the fix should generate
    proposed_serialized = f"{module}.{enum_class.__name__}['{enum_value.name}']"
    proposed_imports = {f'import {module}'}
    
    print(f"Proposed serialized: {proposed_serialized}")
    print(f"Proposed imports: {proposed_imports}")
    
    # Try to reconstruct using the proposed format
    print("\nTrying to execute the proposed serialized code:")
    try:
        exec_globals = {'__main__': __import__('__main__')}
        result = eval(proposed_serialized, exec_globals)
        print(f"Successfully reconstructed: {result}")
        print(f"Equal to original: {result == enum_value}")
        print("SUCCESS: This approach is stable regardless of translation!")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == '__main__':
    test_current_behavior()
    test_proposed_solution()