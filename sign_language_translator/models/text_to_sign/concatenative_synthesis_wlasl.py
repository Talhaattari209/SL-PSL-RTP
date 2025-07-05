"""This module defines the WLASLConcatenativeSynthesis class, which represents 
a rule-based model for translating text to WLASL (Word-Level American Sign Language) 
by concatenating sign language videos and landmarks."""

from __future__ import annotations

import json
import os
import pickle
import random
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from sign_language_translator.config.enums import SignFormats
from sign_language_translator.languages import get_text_language
from sign_language_translator.languages.text import TextLanguage
from sign_language_translator.models.text_to_sign.t2s_model import TextToSignModel
from sign_language_translator.vision.sign.sign import Sign
from sign_language_translator.utils.augmentation import augment_landmarks, preprocess_landmarks


class WLASLConcatenativeSynthesis(TextToSignModel):
    """A class representing a Rule-Based model for translating text to WLASL
    by concatenating sign language videos and landmarks.
    """

    def __init__(
        self,
        text_language: Union[str, TextLanguage] = "english",
        sign_format: str = "landmarks",
        assets_path: Optional[str] = None,
    ) -> None:
        """
        Args:
            text_language (str | TextLanguage): The text language processor object
                or its identifier. Defaults to "english" for WLASL.
            sign_format (str): The sign format to use ("landmarks" or "video").
                Defaults to "landmarks".
            assets_path (str, optional): Path to WLASL assets directory.
                If None, uses default path in sign_language_translator/assets_WLASL.
        """
        self._text_language = None
        self._sign_format = sign_format
        self._assets_path = assets_path or self._get_default_assets_path()
        
        # Initialize mappings and data
        self._wlasl_mappings = {}
        self._psl_to_wlasl_mapping = {}
        self._gloss_to_video_id = {}
        self._video_id_to_gloss = {}
        
        # Load mappings
        self._load_mappings()
        
        # Set text language
        self.text_language = text_language

    def _get_default_assets_path(self) -> str:
        """Get the default path to WLASL assets."""
        current_dir = Path(__file__).parent
        return str(current_dir.parent.parent / "assets_WLASL")

    def _load_mappings(self):
        """Load WLASL mappings and data."""
        mappings_dir = Path(self._assets_path) / "mappings"
        
        # Load PSL to WLASL mapping
        psl_to_wlasl_path = mappings_dir / "psl_to_wlasl_mapping.json"
        if psl_to_wlasl_path.exists():
            with open(psl_to_wlasl_path, 'r', encoding='utf-8') as f:
                self._psl_to_wlasl_mapping = json.load(f)
        
        # Load filtered WLASL data
        filtered_wlasl_path = mappings_dir / "filtered_wlasl.json"
        if filtered_wlasl_path.exists():
            with open(filtered_wlasl_path, 'r', encoding='utf-8') as f:
                wlasl_data = json.load(f)
                
            # Create gloss to video_id mapping
            for entry in wlasl_data:
                gloss = entry["gloss"]
                for instance in entry["instances"]:
                    video_id = instance["video_id"]
                    self._gloss_to_video_id[gloss] = video_id
                    self._video_id_to_gloss[video_id] = gloss

    @property
    def text_language(self) -> TextLanguage:
        """An object of `slt.languages.text.TextLanguage` class that defines preprocessing, tokenization & other NLP functions."""
        if self._text_language is None:
            raise ValueError("Text language is not set.")
        return self._text_language

    @text_language.setter
    def text_language(self, text_language: Union[str, TextLanguage]):
        if isinstance(text_language, str):
            self._text_language = get_text_language(text_language)
        else:
            self._text_language = text_language

    def translate(self, text: str, *args, **kwargs) -> Sign:
        """
        Translate text to WLASL sign language.

        Args:
            text: The input text to be translated.

        Returns:
            The translated sign language sentence.

        """
        # Preprocess text
        text = self.text_language.preprocess(text)
        
        # Tokenize text into words
        words = self.text_language.tokenize(text)
        
        # Map words to WLASL glosses
        glosses = self._map_words_to_glosses(words)
        
        # Get sign segments for each gloss
        sign_segments = self._get_sign_segments(glosses)
        
        # Concatenate sign segments
        if self._sign_format == "landmarks":
            return self._concatenate_landmarks(sign_segments)
        else:
            return self._concatenate_videos(sign_segments)

    def _map_words_to_glosses(self, words: List[str]) -> List[str]:
        """
        Map English words to WLASL glosses.
        
        Args:
            words: List of English words.
            
        Returns:
            List of WLASL glosses.
        """
        glosses = []
        for word in words:
            # Convert to lowercase for matching
            word_lower = word.lower()
            
            # Direct mapping if word exists in WLASL
            if word_lower in self._gloss_to_video_id:
                glosses.append(word_lower)
            else:
                # Try to find a close match or use the original word
                # This is a simple implementation - you might want to add more sophisticated matching
                glosses.append(word_lower)
        
        return glosses

    def _get_sign_segments(self, glosses: List[str]) -> List[Dict]:
        """
        Get sign segments for the given glosses.
        
        Args:
            glosses: List of WLASL glosses.
            
        Returns:
            List of sign segment data.
        """
        segments = []
        
        for gloss in glosses:
            if gloss in self._gloss_to_video_id:
                video_id = self._gloss_to_video_id[gloss]
                segment_data = {
                    "gloss": gloss,
                    "video_id": video_id,
                    "landmarks_path": self._get_landmarks_path(gloss, video_id),
                    "video_path": self._get_video_path(gloss)
                }
                segments.append(segment_data)
            else:
                # Skip glosses that don't have corresponding data
                print(f"Warning: No data found for gloss '{gloss}'")
        
        return segments

    def _get_landmarks_path(self, gloss: str, video_id: str) -> Optional[str]:
        """Get the path to landmarks file for a given gloss."""
        landmarks_dir = Path(self._assets_path) / "Augmented_LandMarks" / "Processed_Landmarks_WLASL"
        
        # Look for the gloss directory
        gloss_dir = landmarks_dir / f"{gloss}_{video_id}"
        if gloss_dir.exists():
            landmarks_file = gloss_dir / "landmarks_preprocessed.pkl"
            if landmarks_file.exists():
                return str(landmarks_file)
        
        # Try alternative naming patterns
        for subdir in landmarks_dir.iterdir():
            if subdir.is_dir() and gloss in subdir.name:
                landmarks_file = subdir / "landmarks_preprocessed.pkl"
                if landmarks_file.exists():
                    return str(landmarks_file)
        
        return None

    def _get_video_path(self, gloss: str) -> Optional[str]:
        """Get the path to video file for a given gloss."""
        videos_dir = Path(self._assets_path) / "Common_WLASL_videos" / "Common_WLASL_videos"
        video_file = videos_dir / f"{gloss}.mp4"
        
        if video_file.exists():
            return str(video_file)
        
        return None

    def _concatenate_landmarks(self, sign_segments: List[Dict]) -> Sign:
        """
        Concatenate landmark segments.
        
        Args:
            sign_segments: List of sign segment data.
            
        Returns:
            Concatenated landmarks as a Sign object.
        """
        concatenated_landmarks = []
        
        for segment in sign_segments:
            landmarks_path = segment.get("landmarks_path")
            if landmarks_path and os.path.exists(landmarks_path):
                try:
                    with open(landmarks_path, 'rb') as f:
                        landmarks = pickle.load(f)
                    
                    # Add landmarks to the sequence
                    if isinstance(landmarks, np.ndarray):
                        concatenated_landmarks.append(landmarks)
                    else:
                        # Handle different landmark formats
                        concatenated_landmarks.append(np.array(landmarks))
                        
                except Exception as e:
                    print(f"Error loading landmarks from {landmarks_path}: {e}")
        
        if concatenated_landmarks:
            # Concatenate all landmark sequences
            final_landmarks = np.concatenate(concatenated_landmarks, axis=0)
            
            # Create a simple Sign object (you might want to use your actual Sign class)
            class LandmarkSign:
                def __init__(self, landmarks):
                    self.landmarks = landmarks
                    self.name = "WLASL_Landmarks"
                
                def __len__(self):
                    return len(self.landmarks)
            
            return LandmarkSign(final_landmarks)
        else:
            raise ValueError("No valid landmarks found for concatenation")

    def _concatenate_videos(self, sign_segments: List[Dict]) -> Sign:
        """
        Concatenate video segments.
        
        Args:
            sign_segments: List of sign segment data.
            
        Returns:
            Concatenated videos as a Sign object.
        """
        # This is a placeholder for video concatenation
        # You would need to implement video concatenation logic here
        # using libraries like OpenCV or moviepy
        
        video_paths = []
        for segment in sign_segments:
            video_path = segment.get("video_path")
            if video_path and os.path.exists(video_path):
                video_paths.append(video_path)
        
        if video_paths:
            # Create a simple Sign object for videos
            class VideoSign:
                def __init__(self, video_paths):
                    self.video_paths = video_paths
                    self.name = "WLASL_Videos"
                
                def __len__(self):
                    return len(self.video_paths)
            
            return VideoSign(video_paths)
        else:
            raise ValueError("No valid videos found for concatenation")

    def get_available_glosses(self) -> List[str]:
        """Get list of available WLASL glosses."""
        return list(self._gloss_to_video_id.keys())

    def get_gloss_count(self) -> int:
        """Get the total number of available WLASL glosses."""
        return len(self._gloss_to_video_id)

    def translate_to_video(self, text: str, output_path: str = "output_wlasl_video.mp4", *args, **kwargs):
        """
        Translate text to WLASL sign language video and save to file.
        Args:
            text: The input text to be translated.
            output_path: Path to save the generated video.
        Returns:
            output_path
        """
        # Ensure sign_format is video
        if self._sign_format != "video":
            raise ValueError("sign_format must be 'video' to output video.")
        sign_video = self.translate(text, *args, **kwargs)
        sign_video.save(output_path)
        return output_path

def wlasl_text_to_sign_pipeline(
    text: str,
    dataset_csv: str,
    landmark_dir: str,
    augment: bool = False,
    preprocess: bool = True,
    augmentation_kwargs: dict = None,
    preprocess_kwargs: dict = None,
) -> np.ndarray:
    """
    Pipeline for WLASL Text to Sign (Landmarks) for UI/API use.
    Args:
        text: Input text string.
        dataset_csv: Path to CSV with video_name,label columns.
        landmark_dir: Directory containing processed landmark folders.
        augment: Whether to apply augmentation to each landmark.
        preprocess: Whether to apply preprocessing to each landmark.
        augmentation_kwargs: Dict of kwargs for augment_landmarks.
        preprocess_kwargs: Dict of kwargs for preprocess_landmarks.
    Returns:
        Numpy array of concatenated (and processed) landmark sequence.
    Raises:
        ValueError if no valid landmark found for any gloss.
    """
    dataset = pd.read_csv(dataset_csv)
    words = text.lower().split()
    landmark_sequences = []
    for word in words:
        match = dataset[dataset['label'].str.lower() == word]
        if not match.empty:
            video_name = match.iloc[0]['video_name']
            folder_path = Path(landmark_dir) / video_name
            processed_pkl = folder_path / 'landmarks_complete_processed.pkl'
            if processed_pkl.exists():
                with open(processed_pkl, 'rb') as f:
                    landmarks = pickle.load(f)
                if augment:
                    landmarks = augment_landmarks(landmarks, **(augmentation_kwargs or {}))
                if preprocess:
                    landmarks = preprocess_landmarks(landmarks, **(preprocess_kwargs or {}))
                landmark_sequences.append(landmarks)
            else:
                raise ValueError(f"Processed file not found for {word} (expected at {processed_pkl})")
        else:
            raise ValueError(f"No matching sign for word '{word}' in dataset.")
    if not landmark_sequences:
        raise ValueError("No landmark sequences generated.")
    # Concatenate
    concatenated = np.concatenate(landmark_sequences, axis=0)
    return concatenated 