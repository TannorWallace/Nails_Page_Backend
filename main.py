from fastapi import FastAPI
from database import Base, engine
from fastapi.staticfiles import StaticFiles
from routers import admin, auth, comments, images
from fastapi.middleware.cors import CORSMiddleware

# build tables on startup
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
#load router endpoint .pys
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(comments.router)
app.include_router(images.router)

@app.get("/")
async def root():
    return {"message": "Ground control to Major Tom!,Can you Hear me, Major Tom!? MAJOR TOM!!!"}