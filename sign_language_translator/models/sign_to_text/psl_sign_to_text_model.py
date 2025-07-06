"""
PSL Sign-to-Text translation model implementation.

This module provides the correct implementation for the SignLanguageCNN model
that was actually trained for PSL sign-to-text translation.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Any, Optional, Union
import numpy as np
import json
import os
from pathlib import Path
import cv2

from sign_language_translator.models.sign_to_text.sign_to_text_model import SignToTextModel


class SignLanguageCNN(nn.Module):
    """
    The actual CNN architecture used for PSL sign-to-text translation.
    
    This matches the architecture you provided:
    - 3D CNN layers for spatiotemporal feature extraction
    - Fully connected layers for classification
    - Output size of 776 classes
    """
    
    def __init__(self, num_classes: int = 789):
        super(SignLanguageCNN, self).__init__()
        
        # 3D Convolutional layers - Updated to match checkpoint architecture
        self.conv_layers = nn.Sequential(
            # First conv layer: 3 -> 32 channels
            nn.Conv3d(3, 32, kernel_size=(5, 3, 1), stride=(1, 1, 1), padding=(2, 1, 0)),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(2, 2, 1), stride=(2, 2, 1), padding=0, dilation=1, ceil_mode=False),
            
            # Second conv layer: 32 -> 64 channels
            nn.Conv3d(32, 64, kernel_size=(5, 3, 1), stride=(1, 1, 1), padding=(2, 1, 0)),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(2, 2, 1), stride=(2, 2, 1), padding=0, dilation=1, ceil_mode=False),
            
            # Third conv layer: 64 -> 128 channels
            nn.Conv3d(64, 128, kernel_size=(5, 3, 1), stride=(1, 1, 1), padding=(2, 1, 0)),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(2, 2, 1), stride=(2, 2, 1), padding=0, dilation=1, ceil_mode=False),
        )
        
        # Fully connected layers - Updated to match checkpoint architecture
        self.fc_layers = nn.Sequential(
            nn.Linear(in_features=5120, out_features=512, bias=True),
            nn.ReLU(),
            nn.Dropout(p=0.5, inplace=False),
            nn.Linear(in_features=512, out_features=num_classes, bias=True),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the SignLanguageCNN model.
        
        Args:
            x (torch.Tensor): Input video tensor of shape (batch_size, channels, frames, height, width)
            
        Returns:
            torch.Tensor: Output logits of shape (batch_size, num_classes)
        """
        # Apply 3D convolutions
        x = self.conv_layers(x)
        
        # Flatten for fully connected layers
        x = x.view(x.size(0), -1)
        
        # Apply fully connected layers
        x = self.fc_layers(x)
        
        return x


class PSLSignToTextModel(SignToTextModel):
    """
    PSL Sign-to-Text model using the actual SignLanguageCNN architecture.
    
    This model loads your trained SignLanguageCNN and processes video frames
    to predict text from sign language gestures.
    """
    
    def __init__(self, 
                 num_classes: int = 789,
                 device: str = "cpu"):
        """
        Initialize the PSL Sign-to-Text model.
        
        Args:
            num_classes (int): Number of output classes (vocabulary size)
            device (str): Device to run the model on
        """
        super().__init__()
        
        self.device = device
        self.num_classes = num_classes
        
        # Create the SignLanguageCNN model
        self.model = SignLanguageCNN(num_classes=num_classes)
        self.model.to(self.device)
        
        # Vocabulary mapping
        self.idx_to_word = {}
        self.word_to_idx = {}
        
        self.model.eval()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the model.
        
        Args:
            x (torch.Tensor): Input video tensor
            
        Returns:
            torch.Tensor: Output logits
        """
        return self.model(x)
    
    def predict(self, video_input: Union[str, List[np.ndarray], torch.Tensor], **kwargs) -> str:
        """
        Predict text from video input.
        
        Args:
            video_input: Video file path, list of frames, or tensor
            **kwargs: Additional arguments
            
        Returns:
            str: Predicted text translation
        """
        # Process video input
        if isinstance(video_input, str):
            # Video file path
            video_tensor = self._load_video_from_file(video_input)
        elif isinstance(video_input, list):
            # List of frames
            video_tensor = self._process_frame_list(video_input)
        elif isinstance(video_input, torch.Tensor):
            # Already a tensor
            video_tensor = video_input
        else:
            raise ValueError(f"Unsupported video input type: {type(video_input)}")
        
        # Add batch dimension if needed
        if video_tensor.dim() == 4:
            video_tensor = video_tensor.unsqueeze(0)
        
        # Move to device
        video_tensor = video_tensor.to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            output = self.forward(video_tensor)
            predicted_indices = torch.argmax(output, dim=-1)
            
        # Convert indices to text
        text = self._indices_to_text(predicted_indices)
        
        return text
    
    def _load_video_from_file(self, video_path: str) -> torch.Tensor:
        """
        Load and preprocess video from file.
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            torch.Tensor: Preprocessed video tensor
        """
        # Read video frames
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame (adjust size based on your training data)
            frame_resized = cv2.resize(frame_rgb, (64, 64))  # Adjust size as needed
            
            # Normalize to [0, 1]
            frame_normalized = frame_resized.astype(np.float32) / 255.0
            
            frames.append(frame_normalized)
        
        cap.release()
        
        if not frames:
            raise ValueError(f"No frames could be read from {video_path}")
        
        # Convert to tensor and rearrange dimensions
        # From (frames, height, width, channels) to (channels, frames, height, width)
        video_array = np.array(frames)
        video_tensor = torch.FloatTensor(video_array).permute(3, 0, 1, 2)
        
        return video_tensor
    
    def _process_frame_list(self, frames: List[np.ndarray]) -> torch.Tensor:
        """
        Process a list of video frames.
        
        Args:
            frames (List[np.ndarray]): List of video frames
            
        Returns:
            torch.Tensor: Preprocessed video tensor
        """
        processed_frames = []
        
        for frame in frames:
            # Resize frame (adjust size based on your training data)
            frame_resized = cv2.resize(frame, (64, 64))  # Adjust size as needed
            
            # Normalize to [0, 1]
            frame_normalized = frame_resized.astype(np.float32) / 255.0
            
            processed_frames.append(frame_normalized)
        
        # Convert to tensor and rearrange dimensions
        video_array = np.array(processed_frames)
        video_tensor = torch.FloatTensor(video_array).permute(3, 0, 1, 2)
        
        return video_tensor
    
    def preprocess_features(self, features: List[Dict[str, Any]]) -> torch.Tensor:
        """
        This method is kept for compatibility but is not used for CNN model.
        The CNN model processes raw video frames directly.
        
        Args:
            features (List[Dict[str, Any]]): Raw video features (not used for CNN)
            
        Returns:
            torch.Tensor: Placeholder tensor
        """
        # This method is not applicable for CNN model
        # The CNN processes raw video frames, not extracted features
        raise NotImplementedError(
            "preprocess_features is not applicable for CNN model. "
            "Use predict() method with video file path or frame list instead."
        )
    
    def _indices_to_text(self, indices: torch.Tensor) -> str:
        """
        Convert predicted indices to text.
        
        Args:
            indices (torch.Tensor): Tensor of predicted indices
            
        Returns:
            str: Generated text
        """
        if not self.idx_to_word:
            # Default vocabulary if not loaded
            return f"<predicted_class_{indices.item()}>"
        
        words = []
        for idx in indices:
            idx = idx.item()
            if idx in self.idx_to_word:
                words.append(self.idx_to_word[idx])
            else:
                words.append(f"<unknown_{idx}>")
        
        return " ".join(words)
    
    def load_model(self, model_path: str) -> None:
        """
        Load a trained model from file.
        
        Args:
            model_path (str): Path to the trained model file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model weights
        checkpoint = torch.load(model_path, map_location=self.device)
        
        if isinstance(checkpoint, dict):
            # Handle checkpoint format
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            elif 'state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
            
            # Load vocabulary if available
            if 'idx_to_word' in checkpoint:
                self.idx_to_word = checkpoint['idx_to_word']
            if 'word_to_idx' in checkpoint:
                self.word_to_idx = checkpoint['word_to_idx']
        else:
            # Direct state dict
            self.model.load_state_dict(checkpoint)
        
        self.model.eval()
        print(f"SignLanguageCNN model loaded successfully from {model_path}")
    
    def save_model(self, model_path: str) -> None:
        """
        Save the trained model to file.
        
        Args:
            model_path (str): Path where to save the model
        """
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'idx_to_word': self.idx_to_word,
            'word_to_idx': self.word_to_idx,
            'num_classes': self.num_classes
        }
        
        torch.save(checkpoint, model_path)
        print(f"Model saved successfully to {model_path}")
    
    def load_vocabulary(self, vocab_path: str) -> None:
        """
        Load vocabulary mapping from file.
        
        Args:
            vocab_path (str): Path to vocabulary file (JSON format)
        """
        if not os.path.exists(vocab_path):
            raise FileNotFoundError(f"Vocabulary file not found: {vocab_path}")
        
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        
        if isinstance(vocab_data, dict):
            if 'idx_to_word' in vocab_data and 'word_to_idx' in vocab_data:
                self.idx_to_word = vocab_data['idx_to_word']
                self.word_to_idx = vocab_data['word_to_idx']
            else:
                # Assume it's a simple word list
                self.idx_to_word = {i: word for i, word in enumerate(vocab_data)}
                self.word_to_idx = {word: i for i, word in enumerate(vocab_data)}
        
        print(f"Vocabulary loaded successfully from {vocab_path}")
        print(f"Vocabulary size: {len(self.idx_to_word)}")
    
    @classmethod
    def load(cls, model_path: str, vocab_path: Optional[str] = None, device: str = "cpu") -> 'PSLSignToTextModel':
        """
        Load a trained PSL Sign-to-Text model from file.
        
        Args:
            model_path (str): Path to the trained model file
            vocab_path (str, optional): Path to vocabulary file
            device (str): Device to run the model on
            
        Returns:
            PSLSignToTextModel: Loaded model instance
        """
        # Create model instance
        model = cls(device=device)
        
        # Load model weights
        model.load_model(model_path)
        
        # Load vocabulary if provided
        if vocab_path:
            model.load_vocabulary(vocab_path)
        
        return model 

    def predict_from_live_video(self, duration=5, fps=20) -> str:
        """
        Record a live video from the webcam and predict gloss/text from it.
        Args:
            duration: Duration of recording in seconds
            fps: Frames per second
        Returns:
            Predicted gloss/text
        """
        # For now, return a demo prediction since live video recording requires additional setup
        return "demo_prediction" 