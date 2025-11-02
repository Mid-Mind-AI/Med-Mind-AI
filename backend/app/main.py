from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calendar as calendar_router
from app.routers import report

app = FastAPI()

# CORS for local Next.js dev servers
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000", "http://localhost:3001"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Mount feature routers
app.include_router(calendar_router.router)
app.include_router(report.router)


@app.get("/")
def health_check():
	return {"status": "ok"}
