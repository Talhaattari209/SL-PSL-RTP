#!/usr/bin/env python3
"""
Test script for PSL Sign-to-Text model integration.

This script tests the integration of the trained PSL SignLanguageCNN model with the
sign language translator framework.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_model_loading():
    """Test if the SignLanguageCNN model can be loaded successfully."""
    print("Testing SignLanguageCNN model loading...")
    
    try:
        from sign_language_translator.models import PSLSignToTextModel
        
        # Check if model file exists
        model_path = "sign_language_model_best.pth"
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            print("Please ensure the trained model file is in the project root directory.")
            return False
        
        # Try to load the model
        model = PSLSignToTextModel.load(model_path, device="cpu")
        print("✅ SignLanguageCNN model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False


def test_model_structure():
    """Test if the SignLanguageCNN model has the expected structure."""
    print("\nTesting SignLanguageCNN model structure...")
    
    try:
        from sign_language_translator.models import PSLSignToTextModel
        
        model = PSLSignToTextModel(device="cpu")
        
        # Check if model has required components
        required_components = ['conv_layers', 'fc_layers']
        for component in required_components:
            if hasattr(model.model, component):
                print(f"✅ {component} component found")
            else:
                print(f"❌ {component} component missing")
                return False
        
        # Check CNN architecture details
        conv_layers = model.model.conv_layers
        fc_layers = model.model.fc_layers
        
        # Check number of conv layers (should be 9: 3 conv + 3 relu + 3 maxpool)
        if len(conv_layers) == 9:
            print("✅ Correct number of conv layers (9)")
        else:
            print(f"❌ Wrong number of conv layers: {len(conv_layers)}")
            return False
        
        # Check number of fc layers (should be 4: linear + relu + dropout + linear)
        if len(fc_layers) == 4:
            print("✅ Correct number of fc layers (4)")
        else:
            print(f"❌ Wrong number of fc layers: {len(fc_layers)}")
            return False
        
        print("✅ SignLanguageCNN model structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing model structure: {e}")
        return False


def test_video_processing():
    """Test video processing functionality."""
    print("\nTesting video processing...")
    
    try:
        from sign_language_translator.models import PSLSignToTextModel
        import numpy as np
        import cv2
        
        model = PSLSignToTextModel(device="cpu")
        
        # Create dummy video frames
        dummy_frames = []
        for i in range(10):  # 10 frames
            # Create a dummy RGB frame (64x64x3)
            frame = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            dummy_frames.append(frame)
        
        # Test video processing
        try:
            video_tensor = model._process_frame_list(dummy_frames)
            
            # Check tensor shape: (channels, frames, height, width)
            expected_shape = (3, 10, 64, 64)
            if video_tensor.shape == expected_shape:
                print("✅ Video processing works correctly!")
                return True
            else:
                print(f"❌ Unexpected video tensor shape: {video_tensor.shape}, expected: {expected_shape}")
                return False
                
        except Exception as e:
            print(f"❌ Error in video processing: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing video processing: {e}")
        return False


def test_model_codes():
    """Test if the model codes are properly registered."""
    print("\nTesting model codes...")
    
    try:
        from sign_language_translator.config.enums import ModelCodes, ModelCodeGroups
        
        # Check if PSL sign-to-text model code exists
        if hasattr(ModelCodes, 'PSL_SIGN_TO_TEXT'):
            print("✅ PSL_SIGN_TO_TEXT model code found")
        else:
            print("❌ PSL_SIGN_TO_TEXT model code missing")
            return False
        
        # Check if it's in the sign-to-text group
        if ModelCodes.PSL_SIGN_TO_TEXT.value in ModelCodeGroups.ALL_SIGN_TO_TEXT_MODELS.value:
            print("✅ Model code is in the correct group")
        else:
            print("❌ Model code is not in the correct group")
            return False
        
        print("✅ Model codes are properly registered!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing model codes: {e}")
        return False


def test_model_loading_utility():
    """Test the model loading utility function."""
    print("\nTesting model loading utility...")
    
    try:
        from sign_language_translator.models import get_model
        from sign_language_translator.config.enums import ModelCodes
        
        # Check if model file exists
        model_path = "sign_language_model_best.pth"
        if not os.path.exists(model_path):
            print(f"⚠️  Model file not found: {model_path}")
            print("Skipping model loading utility test")
            return True
        
        # Try to load using utility function
        model = get_model(
            ModelCodes.PSL_SIGN_TO_TEXT,
            model_path=model_path,
            device="cpu"
        )
        
        if model is not None:
            print("✅ Model loading utility works!")
            return True
        else:
            print("❌ Model loading utility failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing model loading utility: {e}")
        return False


def test_cli_integration():
    """Test if CLI integration is working."""
    print("\nTesting CLI integration...")
    
    try:
        from sign_language_translator.cli import slt
        
        # Check if sign-to-text command exists
        commands = [cmd.name for cmd in slt.commands]
        if 'sign-to-text' in commands:
            print("✅ Sign-to-text CLI command found")
            return True
        else:
            print("❌ Sign-to-text CLI command missing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CLI integration: {e}")
        return False


def main():
    """Run all tests."""
    print("PSL SignLanguageCNN Model Integration Test")
    print("=" * 50)
    
    tests = [
        test_model_codes,
        test_model_structure,
        test_video_processing,
        test_model_loading,
        test_model_loading_utility,
        test_cli_integration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SignLanguageCNN integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 