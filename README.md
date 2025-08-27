# Interactive Story Generator

An AI-powered, choose-your-own-adventure web application that lets users generate, play, save, and analyze interactive stories.

## Features

- **AI-Generated Stories**  
  Create unique, themed narratives using GPT-powered prompts.

- **User Authentication**  
  Sign up, log in, and maintain personalized sessions with JWT auth.

- **Save & Load Progress**  
  Save game states (manual & auto-save) and load them later.

- **Analytics Dashboard**  
  Track engagement metrics: stories started, choices made, completion & winning rates.

- **Thematic Illustrations**  
  AI-generated images accompany each story for enhanced immersion.

## Tech Stack

- **Frontend**: React, Vite, React Router, Context API, Axios  
- **Backend**: FastAPI, SQLAlchemy, SQLite (Dev)  
- **Authentication**: JWT, OAuth  
- **AI**: LangChain & GPT-4 via Euron AI  
- **Analytics**: Custom FastAPI endpoints, SQL `analytics_events` table  
- **Deployment**: Docker, GitHub Actions, Google Cloud Run (planned)

## Folder Structure

