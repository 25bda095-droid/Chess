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
from .celery_worker import analyze_game_mistakes

# Setup sys.path to allow imports from engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board
from explanation.llm_integration import LLMExplainer
import chess

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
explainer = LLMExplainer()

class MoveRequest(BaseModel):
    fen: str

class GameFinishRequest(BaseModel):
    opponent_name: Optional[str] = None
    result: str
    pgn: str

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
    try:
        board = Board(fen)
        policy_probs = agent.search_and_get_policy(board)
        
        # Best move based on policy probs
        best_move = max(policy_probs, key=policy_probs.get) if policy_probs else "e2e4"
        
        # Get evaluation in CP
        _, val = agent.evaluate_board(board)
        stm_is_white = board._board.turn == chess.WHITE
        white_val = val if stm_is_white else -val
        eval_score = round(white_val * 10.0, 2) # Represent value in pawns roughly
        
        return {"evaluation": eval_score, "fen": fen, "best_move": best_move}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/api/explanation")
async def get_explanation(fen: str, move: Optional[str] = None):
    """
    Endpoint for fetching explanations.
    """
    try:
        board = Board(fen)
        
        if not move:
            policy_probs = agent.search_and_get_policy(board)
            move = max(policy_probs, key=policy_probs.get) if policy_probs else "e2e4"
            
        _, val = agent.evaluate_board(board)
        stm_is_white = board._board.turn == chess.WHITE
        white_val = val if stm_is_white else -val
        eval_score = f"{white_val * 10.0:+.2f}"
        
        # Use move as simple PV data
        pv_data = move
        
        explanation = await explainer.generate_explanation(
            fen=fen,
            score=eval_score,
            best_move=move,
            pv_data=pv_data
        )
        return {"explanation": explanation, "fen": fen, "move": move}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

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

@app.post("/api/games", response_model=GameResponse)
async def finish_game(
    request: GameFinishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint for saving a finished game and triggering background analysis.
    """
    new_game = Game(
        user_id=current_user.id,
        opponent_name=request.opponent_name,
        result=request.result,
        pgn=request.pgn
    )
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)

    # Dispatch celery task
    analyze_game_mistakes.delay(new_game.id, new_game.pgn)
    
    return new_game

