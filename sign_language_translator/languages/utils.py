"""utility functions for language objects"""

from __future__ import annotations

from typing import TYPE_CHECKING, Union
import json
import pandas as pd
from pathlib import Path

from sign_language_translator.config.enums import (
    SignLanguages,
    TextLanguages,
    normalize_short_code,
)
from sign_language_translator.languages.sign import PakistanSignLanguage
from sign_language_translator.languages.text import English, Hindi, Urdu

if TYPE_CHECKING:
    from enum import Enum

    from sign_language_translator.languages.sign import SignLanguage
    from sign_language_translator.languages.text import TextLanguage


# TODO: AbstractFactory to store str to class mappings
def get_text_language(language_name: Union[str, Enum]) -> TextLanguage:
    """
    Retrieves a TextLanguage object based on the provided language name.

    Args:
        language_name (str): The name of the language.

    Returns:
        TextLanguage: An instance of the TextLanguage class corresponding to the provided language name.

    Raises:
        ValueError: If no TextLanguage class is known for the provided language name.
    """

    code_to_class = {
        TextLanguages.URDU.value: Urdu,
        TextLanguages.HINDI.value: Hindi,
        TextLanguages.ENGLISH.value: English,
    }

    class_ = code_to_class.get(normalize_short_code(language_name), None)
    if class_:
        return class_()  # constructor called

    # Unknown
    raise ValueError(f"no text language class known for '{language_name = }'")


def get_sign_language(language_name: Union[str, Enum]) -> SignLanguage:
    """
    Retrieves a SignLanguage object based on the provided language name.

    Args:
        language_name (str): The name of the language.

    Returns:
        SignLanguage: An instance of SignLanguage class corresponding to the provided language name.

    Raises:
        ValueError: If no SignLanguage class is known for the provided language name.
    """

    code_to_class = {
        SignLanguages.PAKISTAN_SIGN_LANGUAGE.value: PakistanSignLanguage,
    }

    class_ = code_to_class.get(normalize_short_code(language_name), None)
    if class_:
        return class_()  # constructor called

    # Unknown
    raise ValueError(f"no sign language class known for '{language_name = }'")


class BilingualGlossMapper:
    def __init__(self,
                 psl_to_english_path: str = None,
                 wlasl_dataset_csv: str = None):
        # Load PSL to English mapping
        if psl_to_english_path is None:
            psl_to_english_path = str(Path(__file__).parent.parent / 'assets_WLASL/mappings/psl_to_wlasl_mapping.json')
        with open(psl_to_english_path, 'r', encoding='utf-8') as f:
            self.psl_to_english = json.load(f)
        # Invert for English to PSL
        self.english_to_psl = {}
        for k, v in self.psl_to_english.items():
            self.english_to_psl.setdefault(v, []).append(k)
        # Load WLASL dataset CSV
        if wlasl_dataset_csv is None:
            wlasl_dataset_csv = str(Path(__file__).parent.parent / 'assets_WLASL/Augmented_LandMarks/Procesed_LandMark/Processed_Landmarks_WLASL/augmented_dataset.csv')
        self.wlasl_df = pd.read_csv(wlasl_dataset_csv)
        # English to WLASL video
        self.english_to_wlasl_video = {}
        self.wlasl_video_to_english = {}
        for _, row in self.wlasl_df.iterrows():
            video = row['video_name']
            gloss = row['label'].lower()
            self.english_to_wlasl_video.setdefault(gloss, []).append(video)
            self.wlasl_video_to_english[video] = gloss

    def psl_to_english_gloss(self, psl_gloss: str) -> str:
        return self.psl_to_english.get(psl_gloss)

    def english_to_psl_glosses(self, english_gloss: str) -> list:
        return self.english_to_psl.get(english_gloss, [])

    def english_to_wlasl_videos(self, english_gloss: str) -> list:
        return self.english_to_wlasl_video.get(english_gloss.lower(), [])

    def wlasl_video_to_english_gloss(self, video_name: str) -> str:
        return self.wlasl_video_to_english.get(video_name)

    def map_gloss(self, source_lang: str, target_lang: str, gloss: str):
        # Supported langs: 'psl', 'english', 'wlasl_video'
        if source_lang == 'psl' and target_lang == 'english':
            return self.psl_to_english_gloss(gloss)
        if source_lang == 'english' and target_lang == 'psl':
            return self.english_to_psl_glosses(gloss)
        if source_lang == 'english' and target_lang == 'wlasl_video':
            return self.english_to_wlasl_videos(gloss)
        if source_lang == 'wlasl_video' and target_lang == 'english':
            return self.wlasl_video_to_english_gloss(gloss)
        # PSL -> WLASL video
        if source_lang == 'psl' and target_lang == 'wlasl_video':
            eng = self.psl_to_english_gloss(gloss)
            return self.english_to_wlasl_videos(eng) if eng else []
        # WLASL video -> PSL
        if source_lang == 'wlasl_video' and target_lang == 'psl':
            eng = self.wlasl_video_to_english_gloss(gloss)
            return self.english_to_psl_glosses(eng) if eng else []
        return None


class BilingualSignLanguageSystem:
    def __init__(self, psl_to_english_path=None, wlasl_dataset_csv=None):
        self.mapper = BilingualGlossMapper(psl_to_english_path, wlasl_dataset_csv)
        # TODO: Initialize your sign-to-text and text-to-sign models here
        # self.sign_to_text_model = ...
        # self.text_to_sign_model = ...

    def sign_to_text(self, video_name, input_lang='wlasl_video', output_lang='english'):
        # 1. Map input to English gloss
        if input_lang == 'wlasl_video':
            english_gloss = self.mapper.wlasl_video_to_english_gloss(video_name)
        elif input_lang == 'psl':
            english_gloss = self.mapper.psl_to_english_gloss(video_name)
        else:
            english_gloss = video_name  # already English
        # 2. TODO: Run sign-to-text model (use the gloss or video as needed)
        # result = self.sign_to_text_model.predict(...)
        # 3. Map output as needed
        if output_lang == 'psl':
            return self.mapper.english_to_psl_glosses(english_gloss)
        elif output_lang == 'wlasl_video':
            return self.mapper.english_to_wlasl_videos(english_gloss)
        else:
            return english_gloss

    def text_to_sign(self, text, output_lang='wlasl_video'):
        # 1. Map text to English gloss (if needed)
        english_gloss = text.lower()
        # 2. Map to WLASL video or PSL as needed
        if output_lang == 'wlasl_video':
            return self.mapper.english_to_wlasl_videos(english_gloss)
        elif output_lang == 'psl':
            return self.mapper.english_to_psl_glosses(english_gloss)
        else:
            return english_gloss

    def wlasl_to_psl_video(self, wlasl_video_name):
        english_gloss = self.mapper.wlasl_video_to_english_gloss(wlasl_video_name)
        psl_glosses = self.mapper.english_to_psl_glosses(english_gloss)
        # If you have PSL video dataset, map psl_gloss to PSL video here
        return psl_glosses


__all__ = [
    "get_text_language",
    "get_sign_language",
]
