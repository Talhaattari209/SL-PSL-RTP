"""
Module for Sign-to-Sign translation integration (PSL <-> WLASL).
Chains sign-to-text and text-to-sign models to translate a sign video from one language to another.
"""

from typing import Union
import cv2

class SignToSignTranslator:
    """
    Provides a unified interface for sign-to-sign translation between PSL and WLASL.
    Usage:
        translator = SignToSignTranslator(
            psl_sign_to_text_model, wlasl_sign_to_text_model,
            psl_text_to_sign_model, wlasl_text_to_sign_model
        )
        output_path = translator.translate(
            input_video_path, source_lang="psl", target_lang="wlasl"
        )
    """
    def __init__(
        self,
        psl_sign_to_text_model,
        wlasl_sign_to_text_model,
        psl_text_to_sign_model,
        wlasl_text_to_sign_model,
    ):
        self.psl_sign_to_text_model = psl_sign_to_text_model
        self.wlasl_sign_to_text_model = wlasl_sign_to_text_model
        self.psl_text_to_sign_model = psl_text_to_sign_model
        self.wlasl_text_to_sign_model = wlasl_text_to_sign_model

    def translate(
        self,
        input_video: Union[str, list],
        source_lang: str,
        target_lang: str,
        output_path: str = "output_sign_to_sign.mp4"
    ) -> str:
        """
        Translates a sign language video from source_lang to target_lang.
        Args:
            input_video: Path to video file or list of frames (np.ndarray)
            source_lang: "psl" or "wlasl"
            target_lang: "psl" or "wlasl"
            output_path: Path to save the generated target sign video
        Returns:
            Path to the generated target sign video
        """
        # 1. Video to gloss
        if source_lang == "psl":
            gloss = self.psl_sign_to_text_model.predict(input_video)
        elif source_lang == "wlasl":
            frames = input_video
            if isinstance(input_video, str):
                # Load frames from video file
                cap = cv2.VideoCapture(input_video)
                frames = []
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frames.append(frame)
                cap.release()
            gloss = self.wlasl_sign_to_text_model.predict(frames)
        else:
            raise ValueError("Unsupported source language: must be 'psl' or 'wlasl'")

        # 2. Gloss to target sign video
        if target_lang == "psl":
            sign_video = self.psl_text_to_sign_model.translate(gloss)
        elif target_lang == "wlasl":
            sign_video = self.wlasl_text_to_sign_model.translate(gloss)
        else:
            raise ValueError("Unsupported target language: must be 'psl' or 'wlasl'")

        # 3. Save and return path
        sign_video.save(output_path)
        return output_path 