from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware



import user_routes
import recommendation

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
