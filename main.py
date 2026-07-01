from fastapi import FastAPI
from database import Base, engine
from fastapi.staticfiles import StaticFiles
from routers import admin, auth, comments, images
from fastapi.middleware.cors import CORSMiddleware

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    debug=True,
    title="Nail Art Portfolio API",
    description="Backend for Nails by Mykala"
)

# CORS - Allow your Vercel frontend + localhost for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nails-by-mykala.vercel.app",   # Production
        "https://*.vercel.app",                 # All Vercel previews (optional)
        "http://localhost:3000",                # Local dev
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (uncomment if you still need local static serving)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(comments.router)
app.include_router(images.router)

@app.get("/")
async def root():
    return {"message": "Ground control to Major Tom! Can you hear me, Major Tom? MAJOR TOM!!!"}