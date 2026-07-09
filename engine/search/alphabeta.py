import time
import os
import torch
from typing import Optional, Tuple
import chess
from engine.core.board import Board
from engine.nnue.network import NNUE
from engine.nnue.features import HalfKPFeatures

# Constants for infinity
INF = int(1e9)

# Global NNUE variables for efficiency
_nnue_model = None
_nnue_device = torch.device('cpu')

def _load_nnue_model():
    global _nnue_model
    if _nnue_model is None:
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'nnue_base_model_final.pth')
        _nnue_model = NNUE(input_size=41024, embedding_size=32, hidden_size=16)
        _nnue_model.load_state_dict(torch.load(model_path, map_location=_nnue_device, weights_only=True))
        _nnue_model.to(_nnue_device)
        _nnue_model.eval()

@torch.no_grad()
def nnue_evaluate(board: Board) -> int:
    """
    Evaluates the board using the trained NNUE model.
    Returns a score from the perspective of the side to move.
    """
    if board.is_checkmate():
        # Side to move has lost
        return -INF + 1000
    
    if board.is_game_over():
        # Draw (stalemate, etc)
        return 0

    _load_nnue_model()

    sparse_features = HalfKPFeatures.board_to_tensor(board._board)
    dense_features = sparse_features.to_dense()

    if board._board.turn == chess.WHITE:
        feat_stm = dense_features[0].unsqueeze(0)
        feat_nstm = dense_features[1].unsqueeze(0)
    else:
        feat_stm = dense_features[1].unsqueeze(0)
        feat_nstm = dense_features[0].unsqueeze(0)

    score = _nnue_model(feat_stm, feat_nstm).item()
    return int(score)


class AlphaBetaSearch:
    def __init__(self):
        self.nodes_evaluated = 0
        self.stop_search = False
        
        # Warm up the model
        _load_nnue_model()

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
            return nnue_evaluate(board), None

        best_move = None
        legal_moves = board.generate_legal_moves()
        
        if not legal_moves:
            return nnue_evaluate(board), None

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
