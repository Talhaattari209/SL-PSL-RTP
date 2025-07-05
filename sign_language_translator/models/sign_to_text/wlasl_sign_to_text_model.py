"""WLASL Sign-to-Text Model

This module defines the WLASLSignToTextModel class, which represents a neural network model
for translating WLASL (Word-Level American Sign Language) video features to text.
"""

import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2

from sign_language_translator.config.enums import ModelCodes
from sign_language_translator.models.sign_to_text.sign_to_text_model import SignToTextModel


class WLASLSignLanguageCNN(nn.Module):
    """CNN+LSTM architecture for WLASL sign language recognition."""
    
    def __init__(self, num_classes: int, input_channels: int = 3, sequence_length: int = 30):
        """
        Initialize the WLASL Sign Language CNN model.
        
        Args:
            num_classes: Number of WLASL glosses/classes
            input_channels: Number of input channels (3 for RGB)
            sequence_length: Number of frames in the sequence
        """
        super(WLASLSignLanguageCNN, self).__init__()
        
        self.num_classes = num_classes
        self.input_channels = input_channels
        self.sequence_length = sequence_length
        
        # CNN layers for spatial feature extraction
        self.conv_layers = nn.Sequential(
            # First conv block
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Second conv block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Third conv block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        
        # Calculate the size after CNN layers
        # Assuming input is 64x64, after 3 maxpool layers: 64 -> 32 -> 16 -> 8
        cnn_output_size = 128 * 8 * 8
        
        # LSTM layers for temporal modeling
        self.lstm = nn.LSTM(
            input_size=cnn_output_size,
            hidden_size=256,
            num_layers=2,
            batch_first=True,
            dropout=0.3
        )
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
        
    def forward(self, x):
        """
        Forward pass through the network.
        
        Args:
            x: Input tensor of shape (batch_size, channels, frames, height, width)
            
        Returns:
            Output logits of shape (batch_size, num_classes)
        """
        batch_size, channels, frames, height, width = x.size()
        
        # Reshape for CNN processing: (batch_size * frames, channels, height, width)
        x = x.permute(0, 2, 1, 3, 4).contiguous()
        x = x.view(batch_size * frames, channels, height, width)
        
        # Apply CNN layers
        x = self.conv_layers(x)  # (batch_size * frames, 128, 8, 8)
        
        # Flatten CNN output
        x = x.view(batch_size * frames, -1)  # (batch_size * frames, 128*8*8)
        
        # Reshape for LSTM: (batch_size, frames, features)
        x = x.view(batch_size, frames, -1)
        
        # Apply LSTM
        lstm_out, _ = self.lstm(x)  # (batch_size, frames, 256)
        
        # Take the last LSTM output
        x = lstm_out[:, -1, :]  # (batch_size, 256)
        
        # Apply fully connected layers
        x = self.fc_layers(x)  # (batch_size, num_classes)
        
        return x


class WLASLSignToTextModel(SignToTextModel):
    """WLASL Sign-to-Text translation model."""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu",
        assets_path: Optional[str] = None,
    ):
        """
        Initialize the WLASL Sign-to-Text model.
        
        Args:
            model_path: Path to the trained model weights
            device: Device to run the model on ("cpu" or "cuda")
            assets_path: Path to WLASL assets directory
        """
        self.device = device
        self.assets_path = assets_path or self._get_default_assets_path()
        
        # Load vocabulary and mappings
        self.vocabulary = self._load_vocabulary()
        self.num_classes = len(self.vocabulary)
        
        # Initialize model
        self.model = WLASLSignLanguageCNN(
            num_classes=self.num_classes,
            input_channels=3,
            sequence_length=30  # Adjust based on your data
        )
        
        # Load model weights if provided
        if model_path and os.path.exists(model_path):
            self.load(model_path)
        
        self.model.to(device)
        self.model.eval()
    
    def _get_default_assets_path(self) -> str:
        """Get the default path to WLASL assets."""
        current_dir = Path(__file__).parent
        return str(current_dir.parent.parent.parent / "assets_WLASL")
    
    def _load_vocabulary(self) -> List[str]:
        """Load WLASL vocabulary from the filtered data."""
        try:
            mappings_dir = Path(self._assets_path) / "mappings"
            filtered_wlasl_path = mappings_dir / "filtered_wlasl.json"
            
            if filtered_wlasl_path.exists():
                import json
                with open(filtered_wlasl_path, 'r', encoding='utf-8') as f:
                    wlasl_data = json.load(f)
                
                # Extract unique glosses
                vocabulary = [entry["gloss"] for entry in wlasl_data]
                return sorted(vocabulary)
            else:
                # Fallback vocabulary if file not found
                return ["book", "help", "good", "bad", "yes", "no", "please", "thank_you"]
        except Exception as e:
            print(f"Warning: Could not load WLASL vocabulary: {e}")
            return ["book", "help", "good", "bad", "yes", "no", "please", "thank_you"]
    
    def _process_frame_list(self, frames: List[np.ndarray]) -> torch.Tensor:
        """
        Process a list of video frames into a tensor suitable for the model.
        
        Args:
            frames: List of video frames as numpy arrays
            
        Returns:
            Processed tensor of shape (1, channels, frames, height, width)
        """
        # Resize frames to 64x64 (adjust as needed)
        processed_frames = []
        for frame in frames:
            # Convert to RGB if needed
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # BGR to RGB conversion if needed
                frame = frame[:, :, ::-1]
            
            # Resize to 64x64 (you might want to use cv2.resize)
            # For now, we'll assume frames are already the right size
            processed_frames.append(frame)
        
        # Convert to tensor
        frames_array = np.array(processed_frames)
        frames_tensor = torch.from_numpy(frames_array).float()
        
        # Normalize to [0, 1]
        frames_tensor = frames_tensor / 255.0
        
        # Reshape to (1, channels, frames, height, width)
        frames_tensor = frames_tensor.permute(0, 3, 1, 2).unsqueeze(0)
        
        return frames_tensor
    
    def predict(self, video_frames: List[np.ndarray]) -> str:
        """
        Predict the WLASL gloss for a video sequence.
        
        Args:
            video_frames: List of video frames as numpy arrays
            
        Returns:
            Predicted WLASL gloss
        """
        with torch.no_grad():
            # Process frames
            input_tensor = self._process_frame_list(video_frames)
            input_tensor = input_tensor.to(self.device)
            
            # Get model prediction
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)
            
            # Get predicted class
            predicted_class = torch.argmax(probabilities, dim=1).item()
            
            # Map to vocabulary
            predicted_gloss = self.vocabulary[predicted_class]
            
            return predicted_gloss
    
    def predict_batch(self, video_frames_list: List[List[np.ndarray]]) -> List[str]:
        """
        Predict WLASL glosses for a batch of video sequences.
        
        Args:
            video_frames_list: List of video frame sequences
            
        Returns:
            List of predicted WLASL glosses
        """
        predictions = []
        for frames in video_frames_list:
            prediction = self.predict(frames)
            predictions.append(prediction)
        return predictions
    
    def load(self, model_path: str):
        """Load model weights from file."""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            elif 'state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
                
            print(f"✅ WLASL model loaded successfully from {model_path}")
        except Exception as e:
            print(f"❌ Error loading WLASL model: {e}")
    
    def save(self, model_path: str):
        """Save model weights to file."""
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'vocabulary': self.vocabulary,
                'num_classes': self.num_classes,
            }, model_path)
            print(f"✅ WLASL model saved successfully to {model_path}")
        except Exception as e:
            print(f"❌ Error saving WLASL model: {e}")
    
    @classmethod
    def load(cls, model_path: str, device: str = "cpu", **kwargs) -> "WLASLSignToTextModel":
        """Load a trained WLASL model from file."""
        model = cls(device=device, **kwargs)
        model.load(model_path)
        return model
    
    def get_vocabulary(self) -> List[str]:
        """Get the WLASL vocabulary."""
        return self.vocabulary.copy()
    
    def get_vocabulary_size(self) -> int:
        """Get the size of the WLASL vocabulary."""
        return len(self.vocabulary)
    
    def predict_from_video_file(self, video_path: str) -> str:
        """
        Predict the WLASL gloss for a video file.
        Args:
            video_path: Path to the video file
        Returns:
            Predicted WLASL gloss
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        return self.predict(frames) 

    def predict_from_live_video(self, duration=5, fps=20) -> str:
        """
        Record a live video from the webcam and predict gloss/text from it.
        Args:
            duration: Duration of recording in seconds
            fps: Frames per second
        Returns:
            Predicted gloss/text
        """
        from sign_language_translator.vision.video.video import record_live_video
        video_path = record_live_video(duration=duration, fps=fps)
        return self.predict_from_video_file(video_path)
    
    