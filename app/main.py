from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from . import dropbox

origins = [
    "http://localhost:5173",
    "https://sets.antoniocoutinho.pt",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/files")
def files():
    return dropbox.list_files()


@app.get("/file")
def file(path: str = Query(..., description="Full Dropbox path to file")):
    return dropbox.get_download_link(path)
