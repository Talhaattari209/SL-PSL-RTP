# PSL Sign-to-Text Model Integration

This document explains how to use the integrated PSL (Pakistan Sign Language) Sign-to-Text model with the existing Sign Language Translator framework.

## Overview

The integration adds a complete Sign-to-Text translation pipeline that can:
- Load your trained PSL SignLanguageCNN model (`sign_language_model_best.pth`)
- Process sign language videos directly using 3D CNN
- Translate sign language gestures to text
- Work seamlessly with the existing Text-to-Sign functionality

## Features

- **Model Loading**: Automatic loading of trained PSL SignLanguageCNN models
- **Video Processing**: Direct video frame processing with 3D CNN
- **Text Translation**: CNN-based sign-to-text translation
- **CLI Integration**: Command-line interface for easy usage
- **API Integration**: Python API for programmatic usage

## Installation

1. Ensure your trained model file `sign_language_model_best.pth` is in the project root directory
2. Install the required dependencies:
   ```bash
   pip install torch torchvision opencv-python
   ```

## Usage

### Command Line Interface (CLI)

The easiest way to use the sign-to-text functionality is through the CLI:

```bash
# Basic usage
slt sign-to-text video.mp4

# Use custom model path
slt sign-to-text video.mp4 --model-path /path/to/your/model.pth

# Save output to file
slt sign-to-text video.mp4 --output result.txt

# Use GPU (if available)
slt sign-to-text video.mp4 --device cuda

# Use custom vocabulary file
slt sign-to-text video.mp4 --vocab-path vocabulary.json
```

### Python API

You can also use the sign-to-text functionality programmatically:

```python
from sign_language_translator.models import PSLSignToTextModel

# Load the model
model = PSLSignToTextModel.load(
    model_path="sign_language_model_best.pth",
    vocab_path=None,  # Optional
    device="cpu"
)

# Predict text directly from video file
predicted_text = model.predict("video.mp4")
print(f"Predicted text: {predicted_text}")

# Or predict from a list of frames
import cv2
frames = []
cap = cv2.VideoCapture("video.mp4")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()

predicted_text = model.predict(frames)
print(f"Predicted text: {predicted_text}")
```

### Using the Model Loading Utility

You can also use the built-in model loading utility:

```python
from sign_language_translator.models import get_model
from sign_language_translator.config.enums import ModelCodes

# Load model using the utility function
model = get_model(
    ModelCodes.PSL_SIGN_TO_TEXT,
    model_path="sign_language_model_best.pth",
    vocab_path=None,
    device="cpu"
)

# Use the model
predicted_text = model.predict("video.mp4")
```

## Model Architecture

The PSL Sign-to-Text model uses the **SignLanguageCNN** architecture:

### CNN Architecture
```
SignLanguageCNN(
  (conv_layers): Sequential(
    (0): Conv3d(3, 16, kernel_size=(5, 3, 1), stride=(1, 1, 1), padding=(2, 1, 0))
    (1): ReLU()
    (2): MaxPool3d(kernel_size=(2, 2, 1), stride=(2, 2, 1), padding=0, dilation=1, ceil_mode=False)
    (3): Conv3d(16, 32, kernel_size=(5, 3, 1), stride=(1, 1, 1), padding=(2, 1, 0))
    (4): ReLU()
    (5): MaxPool3d(kernel_size=(2, 2, 1), stride=(2, 2, 1), padding=0, dilation=1, ceil_mode=False)
    (6): Conv3d(32, 64, kernel_size=(5, 3, 1), stride=(1, 1, 1), padding=(2, 1, 0))
    (7): ReLU()
    (8): MaxPool3d(kernel_size=(2, 2, 1), stride=(2, 2, 1), padding=0, dilation=1, ceil_mode=False)
  )
  (fc_layers): Sequential(
    (0): Linear(in_features=6720, out_features=128, bias=True)
    (1): ReLU()
    (2): Dropout(p=0.5, inplace=False)
    (3): Linear(in_features=128, out_features=776, bias=True)
  )
)
```

### Input Features

The model expects:
- **Raw video frames**: RGB video frames (not extracted landmarks)
- **Input shape**: (batch_size, channels=3, frames, height, width)
- **Frame preprocessing**: Resize to 64x64 and normalize to [0, 1]

### Output

The model outputs:
- **Text prediction**: Translated text from sign language
- **Confidence scores**: For each of the 776 classes

## File Structure

```
sign_language_translator/
├── models/
│   ├── sign_to_text/
│   │   ├── __init__.py
│   │   ├── sign_to_text_model.py      # Abstract base class
│   │   ├── psl_sign_to_text_model.py  # SignLanguageCNN implementation
│   │   └── integration_example.py     # Usage examples
│   └── _utils.py                      # Model loading utilities
├── config/
│   └── enums.py                       # Model codes and groups
├── cli.py                             # Command line interface
└── sign_language_model_best.pth       # Your trained model
```

## Configuration

### Model Codes

The integration adds new model codes to the system:
- `psl-sign-to-text`: The PSL SignLanguageCNN sign-to-text translation model

### Model Groups

Sign-to-text models are grouped under:
- `ALL_SIGN_TO_TEXT_MODELS`: All sign-to-text translation models

## Troubleshooting

### Common Issues

1. **Model not found**:
   ```
   Error: Model file not found: sign_language_model_best.pth
   ```
   Solution: Ensure the model file is in the correct location

2. **CUDA out of memory**:
   ```
   RuntimeError: CUDA out of memory
   ```
   Solution: Use `--device cpu` or reduce batch size

3. **Video format not supported**:
   ```
   Error: Could not read video frames
   ```
   Solution: Ensure the video is in a supported format (MP4, AVI, etc.)

4. **Frame size mismatch**:
   ```
   Error: Input tensor size mismatch
   ```
   Solution: The model expects frames resized to 64x64. This is handled automatically.

### Performance Tips

1. **Use GPU**: If available, use `--device cuda` for faster processing
2. **Video optimization**: Use compressed video formats for faster loading
3. **Batch processing**: Process multiple videos in sequence
4. **Frame rate**: The model works with various frame rates

## Integration with Text-to-Sign

The sign-to-text functionality works alongside the existing text-to-sign capabilities:

```python
# Text-to-Sign (existing functionality)
from sign_language_translator.models import ConcatenativeSynthesis
text_to_sign_model = ConcatenativeSynthesis()
sign_video = text_to_sign_model.translate("Hello world")

# Sign-to-Text (new functionality)
from sign_language_translator.models import PSLSignToTextModel
sign_to_text_model = PSLSignToTextModel.load("sign_language_model_best.pth")
predicted_text = sign_to_text_model.predict("sign_video.mp4")
```

## Customization

### Adding Custom Models

To add your own sign-to-text model:

1. Inherit from `SignToTextModel`
2. Implement the required methods
3. Add model code to `enums.py`
4. Update the model loading utility

### Custom Video Preprocessing

You can customize video preprocessing by:
1. Modifying the `_load_video_from_file` method
2. Adjusting frame size (currently 64x64)
3. Changing normalization method
4. Adding custom augmentations

### Vocabulary Management

To use custom vocabulary:
1. Create a JSON file with word mappings
2. Pass the vocabulary path to the model loader
3. The model will use your custom vocabulary for text generation

## Examples

See `sign_language_translator/models/sign_to_text/integration_example.py` for complete usage examples.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the integration example
3. Check the existing documentation
4. Open an issue on the project repository

## License

This integration follows the same license as the main Sign Language Translator project. 