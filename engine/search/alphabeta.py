import time
from typing import Optional, Tuple
import chess
from engine.core.board import Board

# Constants for infinity
INF = int(1e9)

def dummy_evaluate(board: Board) -> int:
    """
    A dummy evaluation function using basic material counting.
    Returns a score from the perspective of the side to move.
    """
    if board.is_checkmate():
        # Side to move has lost
        return -INF + 1000
    
    if board.is_game_over():
        # Draw (stalemate, etc)
        return 0

    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0
    }
    
    score = 0
    for piece_type, value in piece_values.items():
        score += len(board._board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board._board.pieces(piece_type, chess.BLACK)) * value
        
    # Return from the perspective of the side to move
    if board._board.turn == chess.BLACK:
        score = -score
        
    return score


class AlphaBetaSearch:
    def __init__(self):
        self.nodes_evaluated = 0
        self.stop_search = False

    def get_best_move(self, board: Board, max_depth: int = 3, time_limit: Optional[float] = None) -> Optional[chess.Move]:
        """
        Iterative deepening alpha-beta search.
        """
        self.nodes_evaluated = 0
        self.stop_search = False
        start_time = time.time()
        best_move = None

        for depth in range(1, max_depth + 1):
            if self.stop_search:
                break
                
            if time_limit and (time.time() - start_time) > time_limit:
                break

            score, move = self._search(board, depth, -INF, INF, start_time, time_limit)
            
            if not self.stop_search and move is not None:
                best_move = move

        return best_move

    def _search(self, board: Board, depth: int, alpha: int, beta: int, start_time: float, time_limit: Optional[float]) -> Tuple[int, Optional[chess.Move]]:
        self.nodes_evaluated += 1
        
        # Check time limit occasionally
        if self.nodes_evaluated % 1024 == 0 and time_limit:
            if time.time() - start_time > time_limit:
                self.stop_search = True
                return 0, None

        if depth <= 0 or board.is_game_over():
            return dummy_evaluate(board), None

        best_move = None
        legal_moves = board.generate_legal_moves()
        
        if not legal_moves:
            return dummy_evaluate(board), None

        for move in legal_moves:
            if self.stop_search:
                break
                
            board.push(move)
            score, _ = self._search(board, depth - 1, -beta, -alpha, start_time, time_limit)
            score = -score
            board.pop()

            if score > alpha:
                alpha = score
                best_move = move

            if alpha >= beta:
                break  # Beta cut-off

        return alpha, best_move
