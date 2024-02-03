import uvicorn
import os

from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/speech")
async def speak(audio: UploadFile = File(...)):
    return { "filename": audio.filename }


@app.get("/health")
def health() -> None:
    ...


def start():
    port: int = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
