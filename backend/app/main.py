from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calendar as calendar_router
from app.routers import pre_visit_router, report, unified_workflow

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
app.include_router(pre_visit_router.router)
app.include_router(unified_workflow.router)


@app.get("/")
def health_check():
	return {"status": "ok"}
