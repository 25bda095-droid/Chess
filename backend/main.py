import os
import sys
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, Field
from typing import Optional, List, Literal
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import threading
import logging

# Local imports
from .auth import router as auth_router, get_current_user
from .database import get_db
from .models import User, Game, MoveRequest
from .celery_worker import analyze_game_mistakes

# Setup sys.path to allow imports from engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board
from explanation.llm_integration import LLMExplainer
from explanation.tts_commentary import TTSCommentator
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import tempfile
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
agent_lock = threading.Lock()

class GameFinishRequest(BaseModel):
    opponent_name: Optional[str] = Field(default=None, max_length=50)
    result: Literal['win', 'loss', 'draw']
    pgn: str
    
    @field_validator('pgn')
    @classmethod
    def validate_pgn(cls, v: str):
        if not v.strip() or len(v) < 5:
            raise ValueError("Invalid PGN")
        return v

class GameResponse(BaseModel):
    id: int
    user_id: int
    opponent_name: Optional[str] = None
    result: Optional[str] = None
    pgn: Optional[str] = None
    played_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PuzzleResponse(BaseModel):
    fen: str
    solution: List[str]



@app.post("/api/move")
def submit_move(request: MoveRequest):
    """
    Endpoint for submitting a move and getting engine's response.
    """
    try:
        board = Board(request.fen)
        simulations = int(10 + (request.difficulty / 100.0) * 790)
        
        with agent_lock:
            agent.mcts.num_simulations = simulations
            agent.mcts.c_puct = 0.5 + (request.aggression / 50.0)
            policy_probs = agent.search_and_get_policy(board)
            move = agent.sample_move(policy_probs, board)
            
        return {"best_move": move.uci()}
    except Exception as e:
        logging.error(f"Error in submit_move: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/evaluation")
def get_evaluation(fen: str):
    """
    Endpoint for getting engine evaluations.
    """
    try:
        board = Board(fen)
        policy_probs = agent.search_and_get_policy(board)
        
        # Best move based on policy probs
        best_move = max(policy_probs, key=policy_probs.get) if policy_probs else "e2e4"
        
        # Get evaluation in CP
        _, val = agent.evaluate_board(board._board)
        stm_is_white = board._board.turn == chess.WHITE
        white_val = val if stm_is_white else -val
        eval_score = round(white_val * 10.0, 2) # Represent value in pawns roughly
        
        return {"evaluation": eval_score, "fen": fen, "best_move": best_move}
    except Exception as e:
        logging.error(f"Error in get_evaluation: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/explanation")
async def get_explanation(fen: str, move: Optional[str] = None):
    """
    Endpoint for fetching explanations.
    """
    try:
        board = Board(fen)
        
        if move:
            try:
                if chess.Move.from_uci(move) not in board._board.legal_moves:
                    raise ValueError()
            except Exception as e:
                try:
                    parsed_move = board._board.parse_san(move)
                    move = parsed_move.uci()
                except Exception as ex:
                    logging.error(f"Invalid chess move {move}: {ex}", exc_info=True)
                    raise HTTPException(status_code=422, detail="Invalid chess move")
        
        if not move:
            policy_probs = await asyncio.to_thread(agent.search_and_get_policy, board)
            move = max(policy_probs, key=policy_probs.get) if policy_probs else "e2e4"
            
        _, val = await asyncio.to_thread(agent.evaluate_board, board._board)
        stm_is_white = board._board.turn == chess.WHITE
        white_val = val if stm_is_white else -val
        eval_score = f"{white_val * 10.0:+.2f}"
        
        explanation = await explainer.generate_explanation(
            fen=fen,
            score=eval_score,
            best_move=move,
            pv_data=""
        )
        return {"explanation": explanation, "fen": fen, "move": move}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in get_explanation: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/commentary/hindi")
async def get_hindi_commentary(fen: str, move: str, context: str = ""):
    try:
        tts = TTSCommentator()
        prompt = tts.generate_prompt(move=move, fen=fen, context=context)
        
        # Use LLM to generate Hindi commentary
        import litellm
        import os
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing API Key for commentary")
            
        messages = [{"role": "user", "content": prompt}]
        response = await litellm.acompletion(
            model=explainer.model_name,
            messages=messages,
            api_key=api_key,
        )
        hindi_text = response.choices[0].message.content
        
        # Create temp file for gTTS
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.close()
        
        # Generate Audio
        await asyncio.to_thread(tts.speak, text=hindi_text, lang="hi", output_file=temp_file.name, play=False)
        
        return FileResponse(
            temp_file.name, 
            media_type="audio/mpeg", 
            filename="commentary.mp3",
            background=BackgroundTask(os.remove, temp_file.name)
        )
    except Exception as e:
        logging.error(f"Error in get_hindi_commentary: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/history", response_model=List[GameResponse])
async def get_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Protected endpoint to get the user's game history.
    """
    try:
        result = await db.execute(
            select(Game).where(Game.user_id == current_user.id).order_by(Game.played_at.desc())
        )
        games = result.scalars().all()
        return games
    except Exception as e:
        logging.error(f"Database failure in get_history: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database failure")

@app.post("/api/games", response_model=GameResponse)
async def finish_game(
    request: GameFinishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint for saving a finished game and triggering background analysis.
    """
    try:
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
    except Exception as e:
        logging.error(f"Failed to save game: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save game")

import random

@app.get("/api/puzzles/random", response_model=PuzzleResponse)
async def get_random_puzzle():
    """
    Endpoint for returning a random puzzle for Puzzle Rush.
    """
    try:
        # Fetching a puzzle from Lichess API as a dynamic real source instead of a hardcoded stub
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://lichess.org/api/puzzle/daily")
            if resp.status_code == 200:
                data = resp.json()
                puzzle = data.get("puzzle", {})
                game = data.get("game", {})
                
                return {
                    "fen": game.get("pgn", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
                    "solution": puzzle.get("solution", [])
                }
            # Fallback in case of network issue
            return {"fen": "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1", "solution": ["e1e8"]}
    except Exception as e:
        logging.error(f"Error fetching puzzle: {e}", exc_info=True)
        # Fallback
        return {"fen": "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1", "solution": ["e1e8"]}
