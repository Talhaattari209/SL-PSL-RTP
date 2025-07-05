from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from sign_language_translator.languages.utils import BilingualSignLanguageSystem
from sign_language_translator.models.text_to_sign.concatenative_synthesis_wlasl import wlasl_text_to_sign_pipeline
import tempfile
import numpy as np

app = FastAPI()
system = BilingualSignLanguageSystem()

@app.post("/convert")
async def convert(
    input_type: str = Form(...),
    output_type: str = Form(...),
    conversion_mode: str = Form(...),
    input_text: str = Form(None),
    video_file: UploadFile = File(None)
):
    # Example: Text to WLASL Landmarks
    if conversion_mode == "text_to_wlasl":
        landmarks = wlasl_text_to_sign_pipeline(
            text=input_text,
            dataset_csv='sign_language_translator/assets_WLASL/Augmented_LandMarks/Procesed_LandMark/Processed_Landmarks_WLASL/augmented_dataset.csv',
            landmark_dir='sign_language_translator/assets_WLASL/Augmented_LandMarks/Procesed_LandMark/Processed_Landmarks_WLASL'
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".npy") as tmp:
            np.save(tmp, landmarks)
            return FileResponse(tmp.name, filename="landmarks.npy")
    # TODO: Add other conversion modes using system.sign_to_text, etc.
    return JSONResponse({"error": "Conversion mode not implemented."}) 