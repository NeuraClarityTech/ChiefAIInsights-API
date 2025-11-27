from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Chief AI Insights API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neuraclaritytech.com", "https://www.neuraclaritytech.com", "https://chiefaiinsights.com", "https://www.chiefaiinsights.com", "*"],  # tighten later
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message":"Chief AI Insights API is running successfully."}
