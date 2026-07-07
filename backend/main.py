from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Chess API")

class MoveRequest(BaseModel):
    move: str
    fen: Optional[str] = None

@app.post("/api/move")
async def submit_move(request: MoveRequest):
    """
    Endpoint for submitting a move.
    """
    return {"status": "success", "move": request.move, "fen": request.fen}

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
