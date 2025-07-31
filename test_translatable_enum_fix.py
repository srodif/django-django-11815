#!/usr/bin/env python
"""
Test to verify that the enum serialization fix works for translatable enums.
This addresses the issue where migration files would break when enum values
contain translatable text that changes between languages.
"""

import os
import sys
import enum

# Add Django to path
sys.path.insert(0, '/home/runner/work/django-django-11815/django-django-11815')

import django
from django.conf import settings
from django.utils import translation

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
        LANGUAGES=[
            ('en', 'English'),
            ('es', 'Spanish'),
        ],
        LANGUAGE_CODE='en',
    )

django.setup()

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.migrations.serializer import serializer_factory


class Status(enum.Enum):
    GOOD = _('Good')  # This will be translated to different languages
    BAD = _('Bad')    # This will be translated to different languages

    def __str__(self):
        return self.name


def test_enum_serialization_across_languages():
    """
    Test that enum serialization works consistently across different languages.
    The old approach would break when the language changed, but the new approach
    should be stable.
    """
    print("Testing enum serialization across different languages:")
    print("=" * 60)
    
    # Test in English
    with translation.override('en'):
        print(f"\nTesting in English:")
        enum_value = Status.GOOD
        print(f"Enum value: {enum_value}")
        print(f"Enum name: {enum_value.name}")
        print(f"Enum value.value: {enum_value.value}")
        
        serializer = serializer_factory(enum_value)
        serialized_en, imports_en = serializer.serialize()
        print(f"Serialized: {serialized_en}")
        print(f"Imports: {imports_en}")
        
        # Test if the serialized form can be executed
        try:
            exec_globals = {'__main__': __import__('__main__')}
            result_en = eval(serialized_en, exec_globals)
            print(f"Successfully reconstructed: {result_en}")
            print(f"Equal to original: {result_en == enum_value}")
        except Exception as e:
            print(f"ERROR: {e}")

    # Test in Spanish (simulated - we don't have actual translations setup)
    # The key point is that the serialized form should be the same regardless of language
    with translation.override('es'):
        print(f"\nTesting in Spanish:")
        enum_value = Status.GOOD
        print(f"Enum value: {enum_value}")
        print(f"Enum name: {enum_value.name}")
        print(f"Enum value.value: {enum_value.value}")
        
        serializer = serializer_factory(enum_value)
        serialized_es, imports_es = serializer.serialize()
        print(f"Serialized: {serialized_es}")
        print(f"Imports: {imports_es}")
        
        # Test if the serialized form can be executed
        try:
            exec_globals = {'__main__': __import__('__main__')}
            result_es = eval(serialized_es, exec_globals)
            print(f"Successfully reconstructed: {result_es}")
            print(f"Equal to original: {result_es == enum_value}")
        except Exception as e:
            print(f"ERROR: {e}")

    # The key test: serialized forms should be identical regardless of language
    print(f"\nCross-language stability test:")
    print(f"English serialized: {serialized_en}")
    print(f"Spanish serialized:  {serialized_es}")
    print(f"Serializations identical: {serialized_en == serialized_es}")
    
    if serialized_en == serialized_es:
        print("✅ SUCCESS: Enum serialization is stable across languages!")
        print("   Old migration files will work regardless of current language.")
    else:
        print("❌ FAIL: Enum serialization varies with language!")
        print("   This would break old migration files when language changes.")


def test_edge_cases():
    """Test edge cases for enum serialization."""
    print("\n" + "=" * 60)
    print("Testing edge cases:")
    
    # Test enum with special characters in name
    class SpecialEnum(enum.Enum):
        OPTION_A = 'value-a'
        OPTION_B = 'value-b'
    
    print(f"\nEnum with underscores in name:")
    enum_value = SpecialEnum.OPTION_A
    serializer = serializer_factory(enum_value)
    serialized, imports = serializer.serialize()
    print(f"Serialized: {serialized}")
    
    # Test that it can be reconstructed
    try:
        exec_globals = {'__main__': __import__('__main__')}
        result = eval(serialized, exec_globals)
        print(f"Successfully reconstructed: {result}")
        print(f"Equal to original: {result == enum_value}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == '__main__':
    test_enum_serialization_across_languages()
    test_edge_cases()
    print("\n" + "=" * 60)
    print("All tests completed!")