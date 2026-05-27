import uuid
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.genai as genai
import google.genai.types as genai_types
import edge_tts

app = FastAPI(title="Podcast Generator")

AUDIO_DIR = Path("static/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

GEMINI_API_KEY = "AIzaSyA7VmQaBJjY2RS33IetvWSL25viBVAQEdI"

TTS_VOICE = "pt-BR-FranciscaNeural"


_gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def get_client():
    return _gemini_client


class TopicRequest(BaseModel):
    topic: str


class ScriptResponse(BaseModel):
    script: str
    title: str


class AudioResponse(BaseModel):
    audio_url: str
    filename: str


def extract_json(text: str) -> dict:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    data = json.loads(text)
    return {"title": str(data["title"]), "script": str(data["script"])}


def generate_script_from_ai(topic: str) -> dict:
    prompt = (
        f'Crie um roteiro para podcast sobre: "{topic}".\n\n'
        "Regras:\n"
        "- Abertura cativante, 2-3 pontos principais, conclusao com call-to-action\n"
        "- Maximo de 250 palavras no roteiro\n"
        "- Portugues brasileiro, tom descontraido\n\n"
        'Responda SOMENTE com este JSON valido, sem mais nada:\n'
        '{"title": "titulo aqui", "script": "roteiro aqui"}'
    )
    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8192,
        ),
    )
    return extract_json(response.text)


async def text_to_audio_async(text: str, filepath: str):
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    await communicate.save(filepath)


@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path("static/index.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return "<h1>Podcast Generator API</h1>"


@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(request: TopicRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="O tema nao pode estar vazio.")
    try:
        result = generate_script_from_ai(request.topic)
        return ScriptResponse(script=result["script"], title=result["title"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar roteiro: {str(e)}")


@app.post("/generate-audio", response_model=AudioResponse)
async def generate_audio(request: TopicRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Nenhum roteiro fornecido.")
    try:
        filename = f"podcast_{uuid.uuid4().hex[:8]}.mp3"
        filepath = str(AUDIO_DIR / filename)

        await text_to_audio_async(filepath=filepath, text=request.topic)

        return AudioResponse(audio_url=f"/static/audio/{filename}", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar audio: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
