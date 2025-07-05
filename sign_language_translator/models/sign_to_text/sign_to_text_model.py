"""
Abstract base class for sign-to-text translation models.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import torch
import numpy as np

class SignToTextModel(ABC):
    """
    Abstract base class for all sign-to-text translation models.
    
    This class defines the interface that all sign-to-text models must implement.
    """
    
    @abstractmethod
    def predict(self, video_features: Union[List[Dict[str, Any]], torch.Tensor, np.ndarray], **kwargs) -> str:
        """
        Predict text from video features.
        
        Args:
            video_features: Video features extracted from sign language video
            **kwargs: Additional arguments specific to the model
            
        Returns:
            str: Predicted text translation
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """
        Load a trained model from file.
        
        Args:
            model_path (str): Path to the trained model file
        """
        pass
    
    @abstractmethod
    def save_model(self, model_path: str) -> None:
        """
        Save the trained model to file.
        
        Args:
            model_path (str): Path where to save the model
        """
        pass
    
    @abstractmethod
    def preprocess_features(self, features: List[Dict[str, Any]]) -> torch.Tensor:
        """
        Preprocess video features for model input.
        
        Args:
            features (List[Dict[str, Any]]): Raw video features
            
        Returns:
            torch.Tensor: Preprocessed features ready for model input
        """
        pass 