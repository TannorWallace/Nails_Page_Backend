## What I Built

- Full-stack application using **Next.js 16 + FastAPI + PostgreSQL**
- AI-powered nail art generator using **Grok Imagine (xAI)**
- Complete user authentication system with JWT
- Comment system with create, edit, and delete functionality
- Admin dashboard for managing users, images, and comments
- Multiple image upload support for admins
- Clean, reusable component architecture on the frontend
- Database migrations using **Alembic**

## Future Improvements

- Deploy the full application (Frontend on Vercel + Backend with live PostgreSQL)
- Add comment editing UI improvements
- Implement image search and filtering
- Add dark mode support

# Nails by Mykala

**Full-stack nail art portfolio with AI image generation**

A modern, responsive web application built with Next.js + FastAPI that showcases professional nail art, allows users to comment on images, and features an AI-powered nail art generator using Grok Imagine (xAI).

## Features

- **Gallery** – Browse all nail art with swipe navigation and comments
- **AI Nail Art Generator** – Powered by Grok Imagine (xAI) – generate custom designs
- **User Authentication** – Login / Register with JWT
- **Comments System** – Users can post, edit, and delete their own comments
- **Admin Dashboard** – Manage users, images, and all comments
- **Multiple Image Upload** – Admins can upload many images at once
- **Responsive Design** – Fully mobile-friendly with clean UI
- **PostgreSQL + Alembic** – Proper database with migrations

---

## Tech Stack

### Frontend
- **Next.js 16** (App Router)
- **TypeScript**
- **Tailwind CSS v4**
- **React Icons**
- Component-based architecture

### Backend
- **FastAPI**
- **SQLAlchemy 2.0**
- **PostgreSQL** (with Alembic migrations)
- **Pydantic v2**
- **JWT Authentication**
- **Python-dotenv**

### AI
- **Grok Imagine** (xAI API)

---

## Quick Start (Local)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
