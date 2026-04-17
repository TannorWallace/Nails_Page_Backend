from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routers import admin, auth, comments, images   # ← only auth

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI( 
    debug=True,
    title="Nail Art Portfolio API",
    description="Backend for Nails by Mykala"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(comments.router)
app.include_router(images.router)

@app.get("/")
async def root():
    return {"message": "🚀 Nail Art Portfolio Backend is running! Auth ready at /auth"}