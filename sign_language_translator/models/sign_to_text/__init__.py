"""
sign_language_translator.models.sign_to_text
============================================

This module contains models for translating sign language videos to text.

Classes:
    SignToTextModel: Abstract base class for sign-to-text translation models.
    PSLSignToTextModel: A neural network model for translating PSL video features to text.
"""

from sign_language_translator.models.sign_to_text.sign_to_text_model import SignToTextModel
from sign_language_translator.models.sign_to_text.psl_sign_to_text_model import PSLSignToTextModel

__all__ = [
    "SignToTextModel",
    "PSLSignToTextModel",
]
