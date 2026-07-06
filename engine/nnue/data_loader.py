import chess.pgn
import torch
from torch.utils.data import IterableDataset, DataLoader
from features import HalfKPFeatures

class PGNIterableDataset(IterableDataset):
    def __init__(self, pgn_file_path, max_games=None):
        self.pgn_file_path = pgn_file_path
        self.max_games = max_games

    def __iter__(self):
        with open(self.pgn_file_path, "r") as pgn_file:
            games_processed = 0
            while True:
                if self.max_games and games_processed >= self.max_games:
                    break
                
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                
                # Parse game result to use as the training target
                result_str = game.headers.get("Result", "*")
                if result_str == "1-0":
                    target_val = 1.0  # White wins
                elif result_str == "0-1":
                    target_val = -1.0 # Black wins
                elif result_str == "1/2-1/2":
                    target_val = 0.0  # Draw
                else:
                    continue # Skip incomplete or unknown games

                board = game.board()
                for move in game.mainline_moves():
                    # Get the HalfKP sparse tensor for the current position
                    sparse_tensor = HalfKPFeatures.board_to_tensor(board)
                    
                    # Convert to dense for easy batched processing on the GPU
                    dense_tensor = sparse_tensor.to_dense()
                    
                    feat_white = dense_tensor[0]
                    feat_black = dense_tensor[1]
                    
                    # Align features from the perspective of the side-to-move
                    if board.turn == chess.WHITE:
                        feat_stm = feat_white
                        feat_nstm = feat_black
                        target = torch.tensor([target_val], dtype=torch.float32)
                    else:
                        feat_stm = feat_black
                        feat_nstm = feat_white
                        # Invert target because perspective is flipped
                        target = torch.tensor([-target_val], dtype=torch.float32)

                    yield feat_stm, feat_nstm, target
                    
                    # Move to next position
                    board.push(move)
                
                games_processed += 1

def create_pgn_dataloader(pgn_file_path, batch_size=32, max_games=None):
    dataset = PGNIterableDataset(pgn_file_path, max_games)
    return DataLoader(dataset, batch_size=batch_size)
