import os
import uuid
import chess
import chess.svg
import cairosvg

def generate_mistake_screenshot(fen: str, move_played: str, best_move: str, game_id: str) -> str:
    """
    Generate an SVG with arrows (red for move played, green for best move).
    Convert it to a PNG using cairosvg.svg2png and save it to the static directory.
    Return the file path.
    """
    board = chess.Board(fen)
    
    arrows = []
    
    try:
        played = chess.Move.from_uci(move_played)
        arrows.append(chess.svg.Arrow(played.from_square, played.to_square, color="red"))
    except ValueError:
        pass
        
    try:
        best = chess.Move.from_uci(best_move)
        arrows.append(chess.svg.Arrow(best.from_square, best.to_square, color="green"))
    except ValueError:
        pass
        
    svg_data = chess.svg.board(board=board, arrows=arrows)
    
    save_dir = os.path.join(os.path.dirname(__file__), 'static', 'screenshots')
    os.makedirs(save_dir, exist_ok=True)
    
    # We can use game_id and a short uuid to ensure uniqueness
    safe_game_id = os.path.basename(game_id)
    filename = f"{safe_game_id}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(save_dir, filename)
    
    cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=filepath)
    
    return filepath
