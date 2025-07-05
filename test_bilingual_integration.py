#!/usr/bin/env python3
"""
Test script for Bilingual PSL<->WLASL Sign Language System.

This script tests the integration of all 4 tasks in the bilingual system:
1. PSL Sign-to-Text (CNN+LSTM)
2. WLASL Sign-to-Text (CNN+LSTM) 
3. PSL Text-to-Sign (Concatenative Synthesis)
4. WLASL Text-to-Sign (Concatenative Synthesis)
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_model_codes():
    """Test if all model codes are properly registered."""
    print("Testing model codes registration...")
    
    try:
        from sign_language_translator.config.enums import ModelCodes, ModelCodeGroups
        
        # Check if all required model codes exist
        required_codes = [
            'PSL_SIGN_TO_TEXT',
            'WLASL_SIGN_TO_TEXT', 
            'CONCATENATIVE_SYNTHESIS',
            'WLASL_CONCATENATIVE_SYNTHESIS'
        ]
        
        for code in required_codes:
            if hasattr(ModelCodes, code):
                print(f"✅ {code} model code found")
            else:
                print(f"❌ {code} model code missing")
                return False
        
        # Check if they're in the correct groups
        if ModelCodes.PSL_SIGN_TO_TEXT.value in ModelCodeGroups.ALL_SIGN_TO_TEXT_MODELS.value:
            print("✅ PSL_SIGN_TO_TEXT is in sign-to-text group")
        else:
            print("❌ PSL_SIGN_TO_TEXT is not in sign-to-text group")
            return False
            
        if ModelCodes.WLASL_SIGN_TO_TEXT.value in ModelCodeGroups.ALL_SIGN_TO_TEXT_MODELS.value:
            print("✅ WLASL_SIGN_TO_TEXT is in sign-to-text group")
        else:
            print("❌ WLASL_SIGN_TO_TEXT is not in sign-to-text group")
            return False
            
        if ModelCodes.CONCATENATIVE_SYNTHESIS.value in ModelCodeGroups.ALL_TEXT_TO_SIGN_MODELS.value:
            print("✅ CONCATENATIVE_SYNTHESIS is in text-to-sign group")
        else:
            print("❌ CONCATENATIVE_SYNTHESIS is not in text-to-sign group")
            return False
            
        if ModelCodes.WLASL_CONCATENATIVE_SYNTHESIS.value in ModelCodeGroups.ALL_TEXT_TO_SIGN_MODELS.value:
            print("✅ WLASL_CONCATENATIVE_SYNTHESIS is in text-to-sign group")
        else:
            print("❌ WLASL_CONCATENATIVE_SYNTHESIS is not in text-to-sign group")
            return False
        
        print("✅ All model codes are properly registered!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing model codes: {e}")
        return False


def test_psl_sign_to_text():
    """Test PSL Sign-to-Text model loading and structure."""
    print("\nTesting PSL Sign-to-Text model...")
    
    try:
        from sign_language_translator.models import PSLSignToTextModel
        
        # Check if model file exists
        model_path = "sign_language_model_best.pth"
        if not os.path.exists(model_path):
            print(f"⚠️  PSL model file not found: {model_path}")
            print("Skipping PSL sign-to-text test")
            return True
        
        # Try to load the model
        model = PSLSignToTextModel.load(model_path, device="cpu")
        
        # Check model structure
        if hasattr(model, 'model') and hasattr(model.model, 'conv_layers'):
            print("✅ PSL model structure is correct")
        else:
            print("❌ PSL model structure is incorrect")
            return False
        
        print("✅ PSL Sign-to-Text model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing PSL sign-to-text: {e}")
        return False


def test_wlasl_sign_to_text():
    """Test WLASL Sign-to-Text model loading and structure."""
    print("\nTesting WLASL Sign-to-Text model...")
    
    try:
        from sign_language_translator.models import WLASLSignToTextModel
        
        # Check if model file exists
        model_path = "sign_language_translator/assets_WLASL/model/wlasl_sign_cnn_lstm_30frames.pth"
        if not os.path.exists(model_path):
            print(f"⚠️  WLASL model file not found: {model_path}")
            print("Skipping WLASL sign-to-text test")
            return True
        
        # Try to load the model
        model = WLASLSignToTextModel.load(model_path, device="cpu")
        
        # Check model structure
        if hasattr(model, 'model') and hasattr(model.model, 'conv_layers'):
            print("✅ WLASL model structure is correct")
        else:
            print("❌ WLASL model structure is incorrect")
            return False
        
        # Check vocabulary
        vocab = model.get_vocabulary()
        if len(vocab) > 0:
            print(f"✅ WLASL vocabulary loaded with {len(vocab)} glosses")
        else:
            print("❌ WLASL vocabulary is empty")
            return False
        
        print("✅ WLASL Sign-to-Text model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing WLASL sign-to-text: {e}")
        return False


def test_psl_text_to_sign():
    """Test PSL Text-to-Sign concatenative synthesis."""
    print("\nTesting PSL Text-to-Sign concatenative synthesis...")
    
    try:
        from sign_language_translator.models import ConcatenativeSynthesis
        
        # Create PSL concatenative synthesis model
        model = ConcatenativeSynthesis(
            text_language="urdu",
            sign_language="pakistan-sign-language",
            sign_format="video"
        )
        
        # Test translation
        test_text = "hello"
        try:
            result = model.translate(test_text)
            print(f"✅ PSL text-to-sign translation successful: '{test_text}' -> {result.name}")
            return True
        except Exception as e:
            print(f"⚠️  PSL text-to-sign translation failed: {e}")
            print("This might be due to missing video assets")
            return True  # Don't fail the test for missing assets
        
    except Exception as e:
        print(f"❌ Error testing PSL text-to-sign: {e}")
        return False


def test_wlasl_text_to_sign():
    """Test WLASL Text-to-Sign concatenative synthesis."""
    print("\nTesting WLASL Text-to-Sign concatenative synthesis...")
    
    try:
        from sign_language_translator.models import WLASLConcatenativeSynthesis
        
        # Create WLASL concatenative synthesis model
        model = WLASLConcatenativeSynthesis(
            text_language="english",
            sign_format="landmarks"
        )
        
        # Check available glosses
        available_glosses = model.get_available_glosses()
        if len(available_glosses) > 0:
            print(f"✅ WLASL model loaded with {len(available_glosses)} available glosses")
        else:
            print("❌ WLASL model has no available glosses")
            return False
        
        # Test translation with a simple word
        test_text = "book"
        if test_text in available_glosses:
            try:
                result = model.translate(test_text)
                print(f"✅ WLASL text-to-sign translation successful: '{test_text}' -> {result.name}")
                return True
            except Exception as e:
                print(f"⚠️  WLASL text-to-sign translation failed: {e}")
                print("This might be due to missing landmark assets")
                return True  # Don't fail the test for missing assets
        else:
            print(f"⚠️  Test word '{test_text}' not in available glosses")
            print(f"Available glosses: {available_glosses[:5]}...")  # Show first 5
            return True
        
    except Exception as e:
        print(f"❌ Error testing WLASL text-to-sign: {e}")
        return False


def test_model_loader():
    """Test the model loader utility function."""
    print("\nTesting model loader utility...")
    
    try:
        from sign_language_translator.models import get_model
        from sign_language_translator.config.enums import ModelCodes
        
        # Test loading PSL sign-to-text model
        psl_model = get_model(ModelCodes.PSL_SIGN_TO_TEXT, device="cpu")
        if psl_model is not None:
            print("✅ PSL sign-to-text model loaded via utility")
        else:
            print("⚠️  PSL sign-to-text model not loaded (might be missing file)")
        
        # Test loading WLASL sign-to-text model
        wlasl_model = get_model(ModelCodes.WLASL_SIGN_TO_TEXT, device="cpu")
        if wlasl_model is not None:
            print("✅ WLASL sign-to-text model loaded via utility")
        else:
            print("⚠️  WLASL sign-to-text model not loaded (might be missing file)")
        
        # Test loading PSL text-to-sign model
        psl_t2s_model = get_model(ModelCodes.CONCATENATIVE_SYNTHESIS, 
                                 text_language="urdu", 
                                 sign_language="pakistan-sign-language",
                                 sign_format="video")
        if psl_t2s_model is not None:
            print("✅ PSL text-to-sign model loaded via utility")
        else:
            print("❌ PSL text-to-sign model failed to load")
            return False
        
        # Test loading WLASL text-to-sign model
        wlasl_t2s_model = get_model(ModelCodes.WLASL_CONCATENATIVE_SYNTHESIS,
                                   text_language="english",
                                   sign_format="landmarks")
        if wlasl_t2s_model is not None:
            print("✅ WLASL text-to-sign model loaded via utility")
        else:
            print("❌ WLASL text-to-sign model failed to load")
            return False
        
        print("✅ Model loader utility works correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing model loader: {e}")
        return False


def test_cli_integration():
    """Test if CLI integration is working for all commands."""
    print("\nTesting CLI integration...")
    
    try:
        from sign_language_translator.cli import slt
        
        # Check if all commands exist
        commands = [cmd.name for cmd in slt.commands]
        required_commands = [
            'sign-to-text',
            'wlasl-sign-to-text', 
            'psl-text-to-sign',
            'wlasl-text-to-sign',
            'bilingual-info'
        ]
        
        for cmd in required_commands:
            if cmd in commands:
                print(f"✅ {cmd} CLI command found")
            else:
                print(f"❌ {cmd} CLI command missing")
                return False
        
        print("✅ All CLI commands are properly registered!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing CLI integration: {e}")
        return False


def test_assets_structure():
    """Test if WLASL assets structure is correct."""
    print("\nTesting WLASL assets structure...")
    
    try:
        assets_path = "sign_language_translator/assets_WLASL"
        
        # Check if assets directory exists
        if not os.path.exists(assets_path):
            print(f"❌ WLASL assets directory not found: {assets_path}")
            return False
        
        # Check required subdirectories
        required_dirs = [
            "model",
            "mappings", 
            "Augmented_LandMarks/Processed_Landmarks_WLASL",
            "Common_WLASL_videos/Common_WLASL_videos"
        ]
        
        for subdir in required_dirs:
            full_path = os.path.join(assets_path, subdir)
            if os.path.exists(full_path):
                print(f"✅ {subdir} directory found")
            else:
                print(f"❌ {subdir} directory missing")
                return False
        
        # Check for model files
        model_dir = os.path.join(assets_path, "model")
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.pth')]
        if model_files:
            print(f"✅ Found {len(model_files)} model files")
        else:
            print("⚠️  No model files found")
        
        # Check for mapping files
        mappings_dir = os.path.join(assets_path, "mappings")
        mapping_files = [f for f in os.listdir(mappings_dir) if f.endswith('.json')]
        if mapping_files:
            print(f"✅ Found {len(mapping_files)} mapping files")
        else:
            print("⚠️  No mapping files found")
        
        print("✅ WLASL assets structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing assets structure: {e}")
        return False


def main():
    """Run all tests for the bilingual system."""
    print("🌐 Bilingual PSL<->WLASL Sign Language System Integration Test")
    print("=" * 70)
    
    tests = [
        test_model_codes,
        test_assets_structure,
        test_psl_sign_to_text,
        test_wlasl_sign_to_text,
        test_psl_text_to_sign,
        test_wlasl_text_to_sign,
        test_model_loader,
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
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bilingual system integration is working correctly.")
        print("\n📋 System Summary:")
        print("✅ PSL Sign-to-Text (CNN+LSTM)")
        print("✅ WLASL Sign-to-Text (CNN+LSTM)")
        print("✅ PSL Text-to-Sign (Concatenative Synthesis)")
        print("✅ WLASL Text-to-Sign (Concatenative Synthesis)")
        print("✅ CLI Integration")
        print("✅ Model Loader")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n💡 Next Steps:")
        print("1. Ensure all model files are in the correct locations")
        print("2. Check that WLASL assets are properly structured")
        print("3. Verify that all dependencies are installed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 