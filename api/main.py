from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/speak")
async def speak(audio: UploadFile = File(...)):
    return { "filename": audio.filename }
