import os
from celery import Celery
import time

broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Set up Celery app
celery_app = Celery(
    "chess_celery",
    broker=broker_url,
    backend=broker_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

import io
import sys
import chess
import chess.pgn

# Setup sys.path to allow imports from engine and analysis
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analysis.blunder_detection import BlunderDetector
from engine.selfplay.loop import NNUEMCTSAgent

# Instantiate agent globally for the worker to avoid reloading model each time
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nnue_base_model_final.pth'))
agent = None

def get_agent():
    global agent
    if agent is None:
        agent = NNUEMCTSAgent(model_path=model_path, simulations=10) # Lower simulations for faster eval
    return agent

@celery_app.task(name="analyze_game_mistakes")
def analyze_game_mistakes(game_id: int, pgn: str = None):
    """
    Task to asynchronously analyze a finished game for mistakes/blunders.
    """
    if not pgn:
        return {"error": "No PGN provided"}
        
    game = chess.pgn.read_game(io.StringIO(pgn))
    if game is None:
        return {"error": "Invalid PGN"}
        
    engine_agent = get_agent()
    detector = BlunderDetector()
    
    board = game.board()
    evaluations = []
    
    for move in game.mainline_moves():
        is_white_move = board.turn == chess.WHITE
        board.push(move)
        
        # Evaluate position
        _, val = engine_agent.evaluate_board(board)
        
        # val is from the perspective of the side to move.
        stm_is_white = board.turn == chess.WHITE
        white_val = val if stm_is_white else -val
        
        # Convert to centipawns (approximate heuristic scaling: 1.0 = 1000 cp)
        centipawns = int(white_val * 1000)
        
        evaluations.append({
            "eval": centipawns,
            "is_white": is_white_move,
            "move": move.uci()
        })
        
    results = detector.analyze_game(evaluations)
    
    blunders = sum(1 for r in results if r['classification'] == 'Blunder')
    mistakes = sum(1 for r in results if r['classification'] == 'Mistake')
    inaccuracies = sum(1 for r in results if r['classification'] == 'Inaccuracy')
    
    return {
        "game_id": game_id,
        "blunders": blunders,
        "mistakes": mistakes,
        "inaccuracies": inaccuracies,
        "details": results
    }
