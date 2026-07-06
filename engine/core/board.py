import chess
from typing import List, Optional

class Board:
    """
    A basic Board representation and move generator wrapper
    using python-chess for initial scaffolding.
    """
    def __init__(self, fen: str = chess.STARTING_FEN):
        self._board = chess.Board(fen)
    
    def reset(self) -> None:
        """Reset the board to the starting position."""
        self._board.reset()
        
    def set_fen(self, fen: str) -> None:
        """Set the board to a specific FEN position."""
        self._board.set_fen(fen)
        
    def get_fen(self) -> str:
        """Get the current FEN representation of the board."""
        return self._board.fen()
        
    def push_uci(self, uci_move: str) -> bool:
        """Push a move in UCI string format. Returns True if successful."""
        try:
            move = chess.Move.from_uci(uci_move)
            if move in self._board.legal_moves:
                self._board.push(move)
                return True
        except ValueError:
            pass
        return False
        
    def push(self, move: chess.Move) -> bool:
        """Push a python-chess Move object. Returns True if successful."""
        if move in self._board.legal_moves:
            self._board.push(move)
            return True
        return False
        
    def pop(self) -> Optional[chess.Move]:
        """Undo the last move and return it."""
        if len(self._board.move_stack) > 0:
            return self._board.pop()
        return None
        
    def generate_legal_moves(self) -> List[chess.Move]:
        """Wrapper for generating legal moves."""
        return list(self._board.legal_moves)
        
    def is_checkmate(self) -> bool:
        """Check if the current position is a checkmate."""
        return self._board.is_checkmate()
        
    def is_stalemate(self) -> bool:
        """Check if the current position is a stalemate."""
        return self._board.is_stalemate()
        
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self._board.is_game_over()
        
    def get_result(self) -> str:
        """Get the game result ('1-0', '0-1', '1/2-1/2', or '*' if ongoing)."""
        return self._board.result()
        
    def __str__(self) -> str:
        """String representation of the board."""
        return str(self._board)
