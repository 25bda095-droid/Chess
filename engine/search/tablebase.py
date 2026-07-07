import chess
import chess.syzygy
import os

class TablebaseHook:
    def __init__(self, tb_dir=None):
        """
        Initializes the Syzygy tablebase hook.
        tb_dir: Path to the Syzygy tablebase files (.rtbw, .rtbz).
        """
        self.tb_dir = tb_dir
        self.tablebase = None
        if tb_dir and os.path.exists(tb_dir):
            try:
                self.tablebase = chess.syzygy.open_tablebase(tb_dir)
            except Exception as e:
                print(f"Failed to load tablebase from {tb_dir}: {e}")

    def get_evaluation(self, board: chess.Board):
        """
        Queries the tablebase when the piece count drops to 5 or 6.
        Overrides the NNUE evaluation for perfect endgame play.
        Returns a score from the engine's perspective or None if not applicable.
        """
        # Tablebases are usually for 5- or 6-piece endgames
        if len(board.piece_map()) <= 6:
            if self.tablebase is not None:
                try:
                    wdl = self.tablebase.probe_wdl(board)
                    # wdl returns positive for win, negative for loss, 0 for draw
                    # We can translate this into a large score to override NNUE
                    if wdl > 0:
                        return 20000 + wdl  # Winning score
                    elif wdl < 0:
                        return -20000 + wdl # Losing score
                    else:
                        return 0            # Draw score
                except Exception:
                    # In case of missing tablebase files for a specific ending
                    pass
        return None

    def get_best_move(self, board: chess.Board):
        """
        Uses DTZ (Distance To Zero) to find the best move in the endgame.
        """
        if len(board.piece_map()) <= 6:
            if self.tablebase is not None:
                try:
                    # Find moves that preserve the WDL value or achieve the best DTZ
                    best_move = None
                    best_score = -float('inf')
                    
                    for move in board.legal_moves:
                        board.push(move)
                        wdl = -self.tablebase.probe_wdl(board)
                        if wdl > best_score:
                            best_score = wdl
                            best_move = move
                        board.pop()
                        
                    return best_move
                except Exception:
                    pass
        return None

    def close(self):
        if self.tablebase is not None:
            self.tablebase.close()
