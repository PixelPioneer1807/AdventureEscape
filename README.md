# AdventureEscape

AdventureEscape is an AI-powered adventure game platform that leverages generative AI to create dynamic, branching narratives and rich visuals. The project is structured with both frontend (React) and backend (Python/FastAPI) components, designed to provide an engaging and extensible escape/adventure experience.

---

## How It Works

### Applied Generative AI (Gaming)

- **Dynamic Story Generation**: The backend employs a Python/LangChain pipeline that interacts with an external LLM (Euriai) to generate interactive, branching adventure stories based on user-selected themes.
- **Visual Asset Creation**: For each narrative node, the system generates two unique visual assets by calling an AI image API. These images are fetched, stored, and served to the frontend, providing visual context for every part of the story.
- **Scalable AI-driven Content**: The architecture allows for dynamic creation of new stories and assets on demand—enabling adaptive, replayable gameplay.

### Analytics and Business Metrics (AI/ML Foundation)

- **Event Tracking**: The backend features a dedicated analytics endpoint that records core player events, such as story start, choices made, and story completion.
- **Business Metrics**: It computes essential metrics like game completion rate and winning rate, providing a data foundation for future analysis, such as player retention modeling.

---

## Project Structure

```
AdventureEscape/
│
├── backend/      # FastAPI backend, story generation, analytics, database, AI/LLM/image integration
├── frontend/     # React frontend for interactive story gameplay
├── README.md     # Project overview and instructions
└── learn.md      # Additional documentation and learning resources
```

---

## Getting Started

### Prerequisites

- Node.js and npm/yarn (for frontend and possibly backend)
- Python 3.x (for backend)
- See individual directories for full dependency requirements

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PixelPioneer1807/AdventureEscape.git
   cd AdventureEscape
   ```

2. **Backend Setup**
   - Navigate to the `backend` directory.
   - Install Python dependencies (see `pyproject.toml`).
   - Setup environment variables for external API keys (LLM, image generation).
   - Run with Uvicorn or your preferred ASGI server.

3. **Frontend Setup**
   - Navigate to the `frontend` directory.
   - Install dependencies with `npm install` or `yarn`.
   - Run locally with `npm start` or `yarn start`.

### Running the Application

- **Backend**: Start the FastAPI server (`uvicorn main:app --reload` in the `backend` directory).
- **Frontend**: Start the React app (`npm start` in the `frontend` directory).

---

## Skills & Features

- AI-generated stories and images for each node (Python, LangChain, external LLM/image APIs)
- RESTful endpoints for story creation, progression, and analytics (FastAPI)
- Analytics for core player events and business metrics
- Frontend integration for seamless interactive storytelling with visuals (React)
- Modular codebase for easy extension and experimentation

---
