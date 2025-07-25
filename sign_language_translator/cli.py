"""
Sign Language Translator (SLT) Command Line Interface

This module provides a command line interface (CLI) for the Sign Language Translator (SLT) library.
It allows you to perform various operations such as translating text to sign language or vice versa,
downloading resource files, completing text sequences using Language Models & embedding videos into
sequences of vectors.

.. code-block:: console

    $ slt
    Usage:
        slt [OPTIONS] COMMAND [ARGS]...

    Options:
        --help  Show this message and exit.

    Commands:
        assets     Assets manager to download & display Datasets & Models.
        complete   Complete a sequence using Language Models.
        translate  Translate text into sign language or vice versa.
        embed      Embed Videos Using Selected Model.
"""

import os
import argparse
import sys
from pathlib import Path

import click
import logging
import cv2
import numpy as np

from sign_language_translator import __version__
from sign_language_translator.models import get_model
from sign_language_translator.config.enums import ModelCodes
from sign_language_translator.models.sign_to_text.wlasl_sign_to_text_model import WLASLSignToTextModel

# TODO: Dockerize the CLI.. but model persistance issue


@click.group()
@click.version_option(__version__)
def slt():
    """
    Sign Language Translator (SLT) command line interface.
    Documentation: https://sign-language-translator.readthedocs.io
    """


@slt.group(no_args_is_help=True)
def assets():
    """
    Assets manager to download & display Datasets & Models.
    """


# Display the assets root directory
@assets.command()
def path():
    """
    Display the assets root directory.
    """

    from sign_language_translator.config.assets import Assets

    click.echo(Assets.ROOT_DIR)


# Display a tree of downloaded resource files
@assets.command()
@click.option(
    "--files",
    "-f",
    default=True,
    show_default=True,
    help="Include files as leaf nodes in the directory tree.",
)
@click.option(
    "--ignore",
    "-i",
    default=[],
    multiple=True,
    show_default=True,
    help="List of regular expressions of file and directory names that should not be displayed.",
)
@click.option(
    "--directory",
    "-d",
    default=None,
    help="Where the asset files are stored. Defaults to 'installation-directory/assets'.",
)
def tree(files, ignore, directory):
    """
    Display a hierarchy of files in the SLT Assets folder.

    Examples:\n
        $ slt assets tree\n
        $ slt assets tree -f false\n
        $ slt assets tree -i ".*\\.mp4" -i ".*\\.csv"
    """

    from sign_language_translator.config.assets import Assets
    from sign_language_translator.utils import tree as display_tree

    if directory:
        Assets.set_root_dir(directory)

    display_tree(Assets.ROOT_DIR, directory_only=not files, ignore=ignore, regex=True)


# Download resource files
@assets.command(no_args_is_help=True)
@click.argument("filenames", nargs=-1, required=True)
@click.option(
    "--overwrite",
    "-o",
    default=False,
    help="Overwrite existing files. Defaults to False.",
)
@click.option(
    "--progress-bar",
    "-p",
    default=True,
    help="Show progress bar for kilobytes downloaded. Defaults to True.",
)
@click.option(
    "--timeout",
    default=20,
    help="Timeout duration for download requests. Defaults to 20 sec.",
)
@click.option(
    "--chunk-size",
    default=131072,
    help="number of bytes to download in each step. Defaults to 131072 or 128K.",
)
@click.option(
    "--directory",
    "-d",
    default=None,
    help="Where to save the downloaded files. Defaults to 'installation-directory/assets'.",
)
def download(filenames, overwrite, progress_bar, timeout, chunk_size, directory):
    """
    Download resource files with regex.

    Downloads package resources matching the given filename regex
    and saves them to the resources folder in installation directory.\n
    Examples:\n
        $ slt download '.*.json' --overwrite true
    """

    from sign_language_translator.config.assets import Assets

    if directory:
        Assets.set_root_dir(directory)

    # Download the specified files
    for filename in filenames:
        success = Assets.download(
            filename,
            overwrite=overwrite,
            progress_bar=progress_bar,
            timeout=timeout,
            chunk_size=chunk_size,
        )
        if success:
            click.echo(f"Downloaded package resource(s) matching: '{filename}'")
        else:
            click.echo(f"Couldn't download package resources matching: '{filename}'")


# Translate
@slt.command(no_args_is_help=True)
@click.argument("inputs", nargs=-1, required=True)
@click.option(
    "--model-code",
    "-m",
    required=True,
    help="Short code to identify the translation model.",
)
@click.option("--text-lang", help="Name of the text language.")
@click.option("--sign-lang", help="Name of the sign language.")
@click.option(
    "--sign-format",
    help="the sign features to be used e.g. 'video', 'landmarks' etc.",
)
@click.option(
    "--sign-embedding-model",
    default=None,
    help="the sign embedding model to be used or which was used (as video preprocessing step) e.g. 'mediapipe-world', 'mediapipe-image'.",
)
@click.option(
    "--output-dir", default=".", help="Output directory for generated translations."
)
@click.option(
    "--overwrite",
    "-o",
    default=False,
    help="Whether to overwrite the target file if it already exists. Defaults to False.",
)
@click.option(
    "--display",
    "-d",
    default=True,
    help="Whether to show the output video. Defaults to True.",
)
@click.option(
    "--save-format",
    default="mp4",
    help="The output file extension. e.g: ('mp4', 'csv', ) Defaults to 'mp4'.",
)
@click.option(
    "--codec",
    default=None,
    help="The output video codec (must be installed on system and configured in OpenCV). e.g: ('h264', 'avc1', 'xvid', 'mp4v', ...). Defaults to None.",
)
def translate(
    inputs,
    model_code,
    text_lang,
    sign_lang,
    sign_format,
    sign_embedding_model,
    output_dir,
    overwrite,
    display,
    save_format,
    codec,
):
    """
    Translate text into sign language or vice versa.

    Translates the given inputs between text and sign language using the specified model and features.
    Currently following model-codes are supported:\n
    1. "concatenative-synthesis" or "rule-based"\n
    Examples:\n
        $ slt translate --model-code rule-based --text-lang urdu --sign-lang psl --sign-format video "ایک سیب اچھا ہے۔"
    """

    from sign_language_translator import get_model, get_sign_wrapper_class
    from sign_language_translator.models import TextToSignModel

    model = get_model(
        model_code=model_code,
        sign_language=sign_lang,
        text_language=text_lang,
        sign_format=sign_format,
        sign_embedding_model=sign_embedding_model,
    )
    if model and isinstance(model, TextToSignModel):  # TODO: , SignToTextModel):
        for text in inputs:
            sign = model.translate(text)
            path_ = os.path.join(output_dir, f"{text}.{save_format}")
            sign.save(path_, overwrite=overwrite, leave=True, codec=codec)
            if display:
                get_sign_wrapper_class(sign.name())(path_).show()

    else:
        click.echo("This type of translation is not yet supported!")


# Complete
@slt.command(no_args_is_help=True)
@click.argument("inputs", nargs=-1, required=True)
@click.option(
    "--model-code",
    "-m",
    required=True,
    help="Short code to identify the language model. You can use multiple models (but of same input type).",
    multiple=True,
)
@click.option(
    "--end-token",
    default=">",
    help="Keep generating until this token.",
    show_default=True,
)
@click.option(
    "--max-length",
    default=20,
    help="Maximum number of tokens to generate.",
    show_default=True,
)
@click.option(
    "--beam-width",
    default=3.0,
    help="Number of possible branches to explore during generation.",
    show_default=True,
)
@click.option(
    "--model-weight",
    "-w",
    default=[1.0],
    multiple=True,
    help="Likelihood of this model getting selected in case multiple models are passed. Defaults to equal probabilities.",
)
@click.option(
    "--selection-strategy",
    default="choose",
    help="In case multiple models are used, should one model be selected at a time for inference ('choose') or should all models be inferred and their output probabilities combined before sampling ('merge').",
    show_default=True,
)
@click.option(
    "--join",
    default=None,
    help="Join the tokens by placing this string inbetween.",
)
def complete(
    inputs,
    model_code,
    end_token,
    max_length,
    beam_width,
    model_weight,
    selection_strategy,
    join,
):
    """
    Complete a sequence using Language Models.

    Predicts next tokens in the given sequence and completes it using the specified model and beam search.
    You can also use multiple models and also pass along model selection weights for each model (using --model-weights).
    Currently you can use the following model-codes:\n
    1. urdu-mixed-ngram (token | start: "<")\n
    2. ur-supported-gpt (token | start: "<")\n
    3. unigram-names (char | start: "[")\n
    4. bigram-names  (char | start: "[a")\n
    5. trigram-names (char | start: "[ab")\n
    Examples:\n
        $ slt complete "<" --model-code urdu-mixed-ngram -w 1.0 --model-code ur-supported-gpt -w 1.5
    """

    from sign_language_translator import get_model
    from sign_language_translator.models import BeamSampling, LanguageModel, MixerLM

    if model_weight == (1,):
        model_weight = [1.0] * len(model_code)
    assert len(model_code) == len(
        model_weight
    ), f"provide 1 weight for every model. Received {model_weight}. Size mismatch: {len(model_code)-len(model_weight)}."

    models = [get_model(model_code=code) for code in model_code]

    if all(isinstance(model, LanguageModel) for model in models):
        sampler = BeamSampling(
            MixerLM(
                models,  # type: ignore
                selection_probabilities=model_weight,
                model_selection_strategy=selection_strategy,
            ),
            beam_width=beam_width,
            end_of_sequence_token=end_token,
            max_length=max_length,
        )

        if models[0].name and "character" in models[0].name:  # type: ignore
            for inp in inputs:
                completion, _ = sampler.complete(inp)
                if isinstance(join, str):
                    completion = join.join(completion)
                click.echo(completion)
        else:
            # assume that all inputs are tokens of same sequence
            completion, _ = sampler.complete(inputs)
            if isinstance(join, str):
                completion = join.join(completion)
            click.echo(completion)

    else:
        click.echo("Model loading failed!")


# Embed
@slt.command(no_args_is_help=True)
@click.argument("inputs", nargs=-1, required=True)
@click.option(
    "--model-code",
    "-m",
    required=True,
    help="Short code to identify the embedding model.",
)
@click.option(
    "--processes",
    default=1,
    help="Number of processes to launch to embed videos using multiprocessing.",
)
@click.option(
    "--embedding-type",
    default="all",
    help="Optional parameter to filter down embeddings if model can return various types. possible values depend on the model. (e.g. 'all', 'world', 'image', 'normalized', 'aligned', 'normalized-aligned')'",
)
@click.option(
    "--output-dir",
    default=".",
    help="where to save the generated embeddings.",
)
@click.option(
    "--save-format",
    default="pt",
    help="What format to save the generated video embeddings in. (e.g. pt, csv, npy, npz). Defaults to 'pt'.",
)
@click.option(
    "--overwrite",
    default=False,
    help="Flag to indicate whether to overwrite existing files. Defaults to False.",
)
# TODO: Precision/format
# @click.option(
#     "--precision",
#     default=4,
#     help="Number of decimal places to save.",
#     show_default=True,
# )
def embed(
    inputs,
    model_code,
    processes: int,
    embedding_type,
    output_dir,
    save_format,
    overwrite,
):
    """
    Embed Videos or Text using selected Model.

    (Video)\n
    Convert video files using a selected embedding model into video embeddings.
    It supports multiple input videos using path patterns and multiprocessing for efficiency.
    --model-codes:\n
    1. mediapipe-pose-2-hand-1\n
    2. mediapipe-pose-1-hand-1\n
    3. mediapipe-pose-0-hand-1\n
    Example:\n
        $ slt embed dataset/*.mp4 --model-code mediapipe-pose-2-hand-1 --embedding-type all --processes 4 --save-format csv\n

    (Text)\n
    Convert text tokens passed as multiple arguments into embedding vectors using the selected model.
    The input args ending with '.txt' are read and split on newline characters.
    Input args ending with '.json' are parsed expected to be an array of strings.
    The output is a pytorch pickled state dict file containing {"tokens": list_of_strings, "vectors": embeddings}\n
    1. lookup-ur-fasttext-cc.pt\n
    Example:\n
        $ slt embed "text" "words" "other-tokens.txt" --model-code en_lookup_ft_cc
    """

    from warnings import warn

    from sign_language_translator import get_model
    from sign_language_translator.models import TextEmbeddingModel, VideoEmbeddingModel

    model = get_model(model_code)

    if isinstance(model, VideoEmbeddingModel):
        from sign_language_translator.models.utils import VideoEmbeddingPipeline

        pipeline = VideoEmbeddingPipeline(model)  # type: ignore

        pipeline.process_videos_parallel(
            inputs,
            n_processes=processes,
            output_dir=output_dir,
            save_format=save_format,
            landmark_type=embedding_type,
            overwrite=overwrite,
        )
    elif isinstance(model, TextEmbeddingModel):
        import json

        import torch

        from sign_language_translator.config.enums import normalize_short_code

        # fix args
        if isinstance(inputs, str):
            inputs = [inputs]
        norm = embedding_type in ("normalized", "normalized-aligned")
        aligned = embedding_type in ("aligned", "normalized-aligned")
        model_code = normalize_short_code(model_code)

        # Parse tokens from inputs
        tokens = []
        for inp in inputs:
            if inp.endswith(".txt"):
                with open(inp, "r") as f:
                    tokens.extend(f.read().splitlines())
            elif inp.endswith(".json"):
                with open(inp, "r") as f:
                    tokens.extend(json.load(f))
            else:
                tokens.append(inp)

        # filter tokens & embed
        filtered_tokens = []
        embeddings = []
        for token in tokens:
            embedding = model.embed(token, pre_normalize=norm, post_normalize=norm, align=aligned)  # type: ignore
            if (embedding == 0).all():
                warn(f"Skipped '{token}' because its not in {model_code} known_tokens.")
            else:
                filtered_tokens.append(token)
                embeddings.append(embedding)

        # save
        embeddings = torch.stack(embeddings)
        target_path = os.path.join(
            output_dir,
            f"{model_code}_{tuple(embeddings.shape)}_embedding.pt".replace(" ", ""),
        )
        if os.path.exists(target_path) and not overwrite:
            raise FileExistsError(f"'{target_path = }' already exists")

        torch.save({"tokens": filtered_tokens, "vectors": embeddings}, target_path)
        click.echo(f"Saved 'tokens' & 'vectors' at {target_path}")

        # TODO: if save_format == "csv":
    else:
        raise ValueError("ERROR: Model loading failed!")


# Sign-to-text command
@slt.command(no_args_is_help=True)
@click.argument("video_path", type=click.Path(exists=True))
@click.option(
    "--model-path",
    default="sign_language_model_best.pth",
    help="Path to the trained PSL sign-to-text model (default: sign_language_model_best.pth)"
)
@click.option(
    "--vocab-path",
    help="Path to vocabulary file (optional)"
)
@click.option(
    "--device",
    default="cpu",
    type=click.Choice(["cpu", "cuda"]),
    help="Device to run the model on (default: cpu)"
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file to save the predicted text"
)
def sign_to_text(video_path, model_path, vocab_path, device, output):
    """
    Translate PSL sign language video to text using the trained CNN+LSTM model.
    
    Example:
        $ slt sign-to-text video.mp4 --model-path model.pth --device cuda
    """
    try:
        import cv2
        import numpy as np
        
        # Load the PSL sign-to-text model
        model = get_model(
            ModelCodes.PSL_SIGN_TO_TEXT,
            model_path=model_path,
            vocab_path=vocab_path,
            device=device
        )
        
        # Load and process video
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        
        if not frames:
            click.echo("❌ No frames found in the video")
            return
        
        # Predict the sign
        predicted_text = model.predict(frames)
        
        # Output result
        click.echo(f"🎯 Predicted PSL Text: {predicted_text}")
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(predicted_text)
            click.echo(f"✅ Result saved to {output}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@slt.command(no_args_is_help=True)
@click.argument("video_path", type=click.Path(exists=True))
@click.option(
    "--model-path",
    default="sign_language_translator/assets_WLASL/model/wlasl_sign_cnn_lstm_30frames.pth",
    help="Path to the trained WLASL sign-to-text model"
)
@click.option(
    "--device",
    default="cpu",
    type=click.Choice(["cpu", "cuda"]),
    help="Device to run the model on (default: cpu)"
)
@click.option(
    "--assets-path",
    help="Path to WLASL assets directory (optional)"
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file to save the predicted text"
)
def wlasl_sign_to_text(video_path, model_path, device, assets_path, output):
    """
    Translate WLASL sign language video to text using the trained CNN+LSTM model.
    
    Example:
        $ slt wlasl-sign-to-text video.mp4 --model-path model.pth --device cuda
    """
    try:
        import cv2
        import numpy as np
        
        # Load the WLASL sign-to-text model
        model = get_model(
            ModelCodes.WLASL_SIGN_TO_TEXT,
            model_path=model_path,
            device=device,
            assets_path=assets_path
        )
        
        # Load and process video
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        
        if not frames:
            click.echo("❌ No frames found in the video")
            return
        
        # Predict the sign
        predicted_text = model.predict(frames)
        
        # Output result
        click.echo(f"🎯 Predicted WLASL Text: {predicted_text}")
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(predicted_text)
            click.echo(f"✅ Result saved to {output}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@slt.command(no_args_is_help=True)
@click.argument("text", type=str)
@click.option(
    "--text-language",
    default="urdu",
    help="Text language (default: urdu)"
)
@click.option(
    "--sign-format",
    default="video",
    type=click.Choice(["video", "landmarks"]),
    help="Output sign format (default: video)"
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file to save the synthesized signs"
)
def psl_text_to_sign(text, text_language, sign_format, output):
    """
    Translate text to PSL sign language using concatenative synthesis.
    
    Example:
        $ slt psl-text-to-sign "hello world" --text-language urdu --sign-format video
    """
    try:
        # Load the PSL text-to-sign model
        model = get_model(
            ModelCodes.CONCATENATIVE_SYNTHESIS,
            text_language=text_language,
            sign_language="pakistan-sign-language",
            sign_format=sign_format
        )
        
        # Translate text to sign
        sign_result = model.translate(text)
        
        # Output result
        click.echo(f"🎯 Input Text: {text}")
        click.echo(f"🎯 Generated PSL Sign: {sign_result.name}")
        click.echo(f"🎯 Sign Length: {len(sign_result)} frames")
        
        if output:
            # Save the sign result (implementation depends on your Sign class)
            if hasattr(sign_result, 'save'):
                sign_result.save(output)
                click.echo(f"✅ Sign saved to {output}")
            else:
                click.echo(f"⚠️  Sign object doesn't have save method")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@slt.command(no_args_is_help=True)
@click.argument("text", type=str)
@click.option(
    "--text-language",
    default="english",
    help="Text language (default: english)"
)
@click.option(
    "--sign-format",
    default="landmarks",
    type=click.Choice(["landmarks", "video"]),
    help="Output sign format (default: landmarks)"
)
@click.option(
    "--assets-path",
    help="Path to WLASL assets directory (optional)"
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file to save the synthesized signs"
)
def wlasl_text_to_sign(text, text_language, sign_format, assets_path, output):
    """
    Translate English text to WLASL sign language using concatenative synthesis.
    
    Example:
        $ slt wlasl-text-to-sign "hello world" --sign-format landmarks
    """
    try:
        # Load the WLASL text-to-sign model
        model = get_model(
            ModelCodes.WLASL_CONCATENATIVE_SYNTHESIS,
            text_language=text_language,
            sign_format=sign_format,
            assets_path=assets_path
        )
        
        # Translate text to sign
        sign_result = model.translate(text)
        
        # Output result
        click.echo(f"🎯 Input Text: {text}")
        click.echo(f"🎯 Generated WLASL Sign: {sign_result.name}")
        click.echo(f"🎯 Sign Length: {len(sign_result)} frames")
        
        if output:
            # Save the sign result (implementation depends on your Sign class)
            if hasattr(sign_result, 'save'):
                sign_result.save(output)
                click.echo(f"✅ Sign saved to {output}")
            else:
                click.echo(f"⚠️  Sign object doesn't have save method")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@slt.command(no_args_is_help=True)
def bilingual_info():
    """
    Display information about the bilingual PSL<->WLASL system.
    """
    click.echo("🌐 Bilingual Sign Language System (PSL <-> WLASL)")
    click.echo("=" * 50)
    click.echo()
    click.echo("📋 Available Tasks:")
    click.echo("1. PSL Sign-to-Text (CNN+LSTM) - slt sign-to-text")
    click.echo("2. WLASL Sign-to-Text (CNN+LSTM) - slt wlasl-sign-to-text")
    click.echo("3. PSL Text-to-Sign (Concatenative Synthesis) - slt psl-text-to-sign")
    click.echo("4. WLASL Text-to-Sign (Concatenative Synthesis) - slt wlasl-text-to-sign")
    click.echo()
    click.echo("🔧 Model Codes:")
    click.echo("- PSL_SIGN_TO_TEXT: PSL sign-to-text translation")
    click.echo("- WLASL_SIGN_TO_TEXT: WLASL sign-to-text translation")
    click.echo("- CONCATENATIVE_SYNTHESIS: PSL text-to-sign translation")
    click.echo("- WLASL_CONCATENATIVE_SYNTHESIS: WLASL text-to-sign translation")
    click.echo()
    click.echo("📚 Examples:")
    click.echo("$ slt sign-to-text video.mp4 --device cuda")
    click.echo("$ slt wlasl-sign-to-text video.mp4 --device cuda")
    click.echo("$ slt psl-text-to-sign 'hello world' --text-language urdu")
    click.echo("$ slt wlasl-text-to-sign 'hello world' --sign-format landmarks")


@click.command('predict-wlasl-sign')
@click.argument('video_path', type=click.Path(exists=True))
@click.option('--model-path', default='wlasl_vit_transformer.pth', help='Path to trained WLASL model (.pth)')
@click.option('--device', default='cpu', help='Device to use (cpu or cuda)')
def predict_wlasl_sign(video_path, model_path, device):
    """Predict the gloss for a WLASL video file using a trained model."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"Loading model from {model_path} on {device}")
    model = WLASLSignToTextModel(model_path=model_path, device=device)
    # Extract frames from video
    logging.info(f"Extracting frames from {video_path}")
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Resize to 64x64 if needed
        frame_resized = cv2.resize(frame, (64, 64))
        frames.append(frame_resized)
    cap.release()
    if not frames:
        logging.error("No frames extracted from video.")
        click.echo("Error: No frames extracted from video.")
        return
    logging.info(f"Extracted {len(frames)} frames. Running prediction...")
    predicted_gloss = model.predict(frames)
    click.echo(f"Predicted gloss: {predicted_gloss}")
    logging.info(f"Prediction complete: {predicted_gloss}")


if __name__ == "__main__":
    slt()
