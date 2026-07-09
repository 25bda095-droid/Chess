# RL-Based Personalized Chess Assistant

An interactive chess assistant powered by a custom reinforcement learning engine. It goes beyond simple engine evaluation by providing natural-language strategic breakdowns and personalized adaptive feedback tailored to an individual's evolving style.

## Architecture

The project is structured into several interconnected modules:

1. **Chess Engine (`engine/`)**: A custom-built chess engine featuring:
   - PyTorch NNUE architecture for state evaluation.
   - Self-play Reinforcement Learning loop.
   - Alpha-beta pruning with iterative deepening and MCTS integration.
2. **Analysis & Explanation (`explanation/`)**: 
   - LLM integration for translating engine analysis into natural language explanations.
   - Grounding validation to prevent LLM hallucinations.
3. **Personalization (`personalization/`)**:
   - Tracks user mistakes to dynamically adjust interaction complexity.
4. **Backend API (`backend/`)**: FastAPI-based REST API handling user authentication, game session persistence (via SQLite/SQLAlchemy), and bridging the frontend with the engine/LLM backend.
5. **Frontend (`frontend/`)**: Modern React application built with Vite, utilizing Glassmorphism UI components for an immersive user experience.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Virtual Environment (recommended)

### Backend & Engine Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd chess
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Copy the `.env.example` file to `.env` and fill in your actual credentials.
   ```bash
   cp .env.example .env
   ```

4. **Start the Backend Server:**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

The frontend should now be running at `http://localhost:5173` and the API backend at `http://localhost:8000`.

## License
[MIT](LICENSE)