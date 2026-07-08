import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Setup sys.path to allow imports from engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board

app = FastAPI(title="Chess API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the agent globally
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nnue_base_model_final.pth'))
agent = NNUEMCTSAgent(model_path=model_path)

class MoveRequest(BaseModel):
    fen: str

@app.post("/api/move")
async def submit_move(request: MoveRequest):
    """
    Endpoint for submitting a move and getting engine's response.
    """
    board = Board(request.fen)
    policy_probs = agent.search_and_get_policy(board)
    move = agent.sample_move(policy_probs, board)
    return {"best_move": move.uci()}

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
