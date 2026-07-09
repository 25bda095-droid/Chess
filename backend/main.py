import os
import sys
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Local imports
from .auth import router as auth_router, get_current_user
from .database import get_db
from .models import User, Game

# Setup sys.path to allow imports from engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board

app = FastAPI(title="Chess API")

# Include the auth router
app.include_router(auth_router)

# Configure CORS dynamically based on environment variables
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173,http://127.0.0.1:5173")
allow_origins = [url.strip() for url in frontend_url.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# Instantiate the agent globally
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nnue_base_model_final.pth'))
agent = NNUEMCTSAgent(model_path=model_path)

class MoveRequest(BaseModel):
    fen: str

class GameResponse(BaseModel):
    id: int
    user_id: int
    opponent_name: Optional[str] = None
    result: Optional[str] = None
    pgn: Optional[str] = None
    played_at: Optional[datetime] = None

    class Config:
        from_attributes = True

@app.post("/api/move")
async def submit_move(request: MoveRequest):
    """
    Endpoint for submitting a move and getting engine's response.
    """
    try:
        board = Board(request.fen)
        policy_probs = agent.search_and_get_policy(board)
        move = agent.sample_move(policy_probs, board)
        return {"best_move": move.uci()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/api/evaluation")
async def get_evaluation(fen: str):
    """
    Endpoint for getting engine evaluations.
    """
    return {"evaluation": 0.0, "fen": fen, "best_move": "e2e4"}

@app.get("/api/explanation")
async def get_explanation(fen: str, move: Optional[str] = None):
    """
    Endpoint for fetching explanations.
    """
    return {"explanation": "This is a placeholder explanation for the move.", "fen": fen, "move": move}

@app.get("/history", response_model=List[GameResponse])
async def get_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Protected endpoint to get the user's game history.
    """
    result = await db.execute(
        select(Game).where(Game.user_id == current_user.id).order_by(Game.played_at.desc())
    )
    games = result.scalars().all()
    return games
