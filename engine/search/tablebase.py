import requests
from typing import Optional

def get_syzygy_move(fen: str) -> Optional[str]:
    """
    Queries the Lichess Syzygy tablebase for the given FEN and returns
    the best move as a UCI string. Returns None on network errors,
    invalid FENs, or if no moves are found.
    """
    try:
        url = "http://tablebase.lichess.ovh/standard"
        response = requests.get(url, params={"fen": fen}, timeout=5.0)
        response.raise_for_status()
        
        data = response.json()
        moves = data.get("moves")
        
        if moves and isinstance(moves, list) and len(moves) > 0:
            return moves[0].get("uci")
            
    except Exception:
        # Gracefully handle timeouts, network errors, invalid FEN responses, etc.
        pass
        
    return None
