from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cloudinary_config

# Import models FIRST so they register with Base
from models import User, ArtImage, Comment
from database import Base, engine

# Now create tables (this will work)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nails by Mykala API", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nails-by-mykala.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import admin, auth, comments, images, ai

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(comments.router)
app.include_router(images.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    return {"message": "Nails by Mykala API is running ✅"}