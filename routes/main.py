from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

import os

import user_routes
import recommendation
import uvicorn
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(recommendation.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}


if __name__=="__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)