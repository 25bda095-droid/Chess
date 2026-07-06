import torch
import chess

class HalfKPFeatures:
    """
    HalfKP (Half King-Piece) feature extractor.
    Features depend on the position of our king and the position of all other pieces.
    There are 41024 features in standard HalfKP:
    (10 piece types x 64 squares) * 64 king squares = 40960
    + 64 king squares = 41024 features.
    
    Piece types: P, N, B, R, Q (white and black) -> 10 types.
    """
    NUM_FEATURES = 41024

    @staticmethod
    def get_piece_index(piece: chess.Piece, pov_color: chess.Color) -> int:
        """
        Returns an index 0-9 for the piece, relative to the point-of-view color.
        """
        # piece.piece_type is 1-6 (PAWN=1, KNIGHT=2, BISHOP=3, ROOK=4, QUEEN=5, KING=6)
        # We ignore Kings here since they are handled by the K part.
        pt_idx = piece.piece_type - 1 # 0 to 4
        
        # 0-4 for friendly, 5-9 for enemy
        is_friendly = (piece.color == pov_color)
        return pt_idx if is_friendly else pt_idx + 5

    @staticmethod
    def get_feature_indices(board: chess.Board, pov_color: chess.Color):
        """
        Get the active feature indices for the given board from the perspective of pov_color.
        """
        king_sq = board.king(pov_color)
        if king_sq is None:
            return [] # Should not happen in standard chess
        
        # Invert squares if perspective is black
        def orient(sq):
            return sq if pov_color == chess.WHITE else chess.square_mirror(sq)
        
        oriented_king_sq = orient(king_sq)
        
        indices = []
        for sq, piece in board.piece_map().items():
            if piece.piece_type == chess.KING:
                continue
            
            p_idx = HalfKPFeatures.get_piece_index(piece, pov_color)
            oriented_sq = orient(sq)
            
            # Feature index calculation
            # p_idx (0-9)
            # oriented_sq (0-63)
            # oriented_king_sq (0-63)
            f_idx = p_idx * 64 * 64 + oriented_sq * 64 + oriented_king_sq
            indices.append(f_idx)
            
        return indices

    @classmethod
    def board_to_tensor(cls, board: chess.Board):
        """
        Converts a chess board into a sparse tensor representing the HalfKP features
        for both white and black perspectives.
        
        Returns:
            A sparse tensor of shape (2, NUM_FEATURES) where [0] is White's perspective
            and [1] is Black's perspective.
        """
        white_indices = cls.get_feature_indices(board, chess.WHITE)
        black_indices = cls.get_feature_indices(board, chess.BLACK)
        
        # Prepare sparse tensor indices and values
        # Shape: (2, NUM_FEATURES)
        # dimensions: [perspective, feature_idx]
        indices = []
        for f_idx in white_indices:
            indices.append([0, f_idx])
        for f_idx in black_indices:
            indices.append([1, f_idx])
            
        if not indices:
            return torch.sparse_coo_tensor(
                torch.empty((2, 0), dtype=torch.long),
                torch.empty(0, dtype=torch.float32),
                size=(2, cls.NUM_FEATURES)
            )

        indices_t = torch.tensor(indices, dtype=torch.long).t()
        values_t = torch.ones(len(indices), dtype=torch.float32)
        
        sparse_tensor = torch.sparse_coo_tensor(
            indices_t, values_t, size=(2, cls.NUM_FEATURES)
        )
        
        return sparse_tensor
