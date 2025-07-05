"""
Integration example for PSL Sign-to-Text model.

This script demonstrates how to use the trained PSL SignLanguageCNN model
with the existing sign language translator framework.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sign_language_translator.models import PSLSignToTextModel


def load_psl_model(model_path: str, vocab_path: str = None, device: str = "cpu"):
    """
    Load the trained PSL SignLanguageCNN model.
    
    Args:
        model_path (str): Path to the trained model file
        vocab_path (str, optional): Path to vocabulary file
        device (str): Device to run the model on
        
    Returns:
        PSLSignToTextModel: Loaded model instance
    """
    print(f"Loading PSL SignLanguageCNN model from {model_path}")
    
    try:
        model = PSLSignToTextModel.load(model_path, vocab_path, device)
        print("Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def predict_text_from_video(model, video_path: str):
    """
    Predict text from a sign language video using the CNN model.
    
    Args:
        model: Loaded PSL SignLanguageCNN model
        video_path (str): Path to the video file
        
    Returns:
        str: Predicted text translation
    """
    print(f"Predicting text from video: {video_path}")
    
    try:
        # The CNN model processes video frames directly
        predicted_text = model.predict(video_path)
        print(f"Predicted text: {predicted_text}")
        return predicted_text
    except Exception as e:
        print(f"Error predicting text: {e}")
        return f"Error: {e}"


def main():
    """
    Main function demonstrating the integration.
    """
    print("PSL SignLanguageCNN Model Integration Example")
    print("=" * 50)
    
    # Model paths
    model_path = "sign_language_model_best.pth"  # Your trained model
    vocab_path = None  # Optional vocabulary file
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("Please ensure the trained model file is in the project root directory.")
        return
    
    # Load model
    model = load_psl_model(model_path, vocab_path, device="cpu")
    if model is None:
        return
    
    # Example usage with a video file
    video_path = "example_psl_video.mp4"  # Replace with your video file
    
    if os.path.exists(video_path):
        predicted_text = predict_text_from_video(model, video_path)
        print(f"\nFinal Result: {predicted_text}")
    else:
        print(f"Video file not found: {video_path}")
        print("Please provide a valid video file path to test the model.")
    
    print("\nIntegration example completed!")


if __name__ == "__main__":
    main() 