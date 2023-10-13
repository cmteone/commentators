from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="commentators",
    description="commentator contexts for cmte.one",
    version="0.1.0",
)

commentator_contexts = {}

class CommentatorContext(BaseModel):
    commentator: str
    context: str

@app.on_event("startup")
async def startup_event():
    global commentator_contexts
    context_dir = Path("./contexts")
    commentators = [file.stem for file in context_dir.glob('*.txt')]

    async def read_file(commentator):
        file_path = context_dir / f"{commentator}.txt"
        with file_path.open('r') as file:
            content = file.read()
            flattened_content = content.replace('\n', ' ')  # Replacing newlines with spaces
            commentator_contexts[commentator] = flattened_content


    await asyncio.gather(*(read_file(commentator) for commentator in commentators))

@app.exception_handler(HTTPException)
def handle_exception(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@app.get("/context/{commentator}", response_model=CommentatorContext)
async def get_context(commentator: str):
    if commentator in commentator_contexts:
        return {"commentator": commentator, "context": commentator_contexts[commentator]}
    else:
        raise HTTPException(status_code=404, detail="Commentator not found")

@app.get("/commentators")
async def get_commentators():
    return {"commentators": list(commentator_contexts.keys())}
