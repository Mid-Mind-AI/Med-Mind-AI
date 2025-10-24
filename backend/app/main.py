from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

cors = CORSMiddleware(
    app=app,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}

