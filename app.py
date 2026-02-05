from fastapi import FastAPI, UploadFile, File, Form
import base64
import math
import collections

app = FastAPI()

SUPPORTED_LANGUAGES = ["english", "hindi", "tamil", "telugu", "kannada"]

def base64_entropy(s):
    freq = collections.Counter(s)
    entropy = 0
    for count in freq.values():
        p = count / len(s)
        entropy -= p * math.log2(p)
    return entropy


@app.post("/detect")
async def detect_voice(
    language: str = Form(...),
    audio: UploadFile = File(...)
):
    language = language.lower()

    if language not in SUPPORTED_LANGUAGES:
        return {
            "error": "Unsupported language",
            "supported_languages": SUPPORTED_LANGUAGES
        }

    # Read uploaded file
    audio_bytes = await audio.read()

    # Convert to base64
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    entropy = base64_entropy(audio_base64)
    length = len(audio_base64)

    ai_score = (entropy * 0.6) + (length / 20000)

    if ai_score > 3.2:
        result = "AI_GENERATED"
        confidence = round(min(0.95, ai_score / 4), 2)
    else:
        result = "HUMAN"
        confidence = round(min(0.9, 1 - (ai_score / 4)), 2)

    return {
        "language": language,
        "result": result,
        "confidence": confidence
    }


@app.get("/")
def root():
    return {
        "status": "AI Voice Detection API running",
        "supported_languages": SUPPORTED_LANGUAGES
    }
